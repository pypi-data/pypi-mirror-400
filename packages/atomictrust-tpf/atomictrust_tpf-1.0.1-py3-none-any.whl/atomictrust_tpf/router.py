#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     TPF-RLM HYBRID ROUTER                                     ║
║            Diffusion Primary with Recursive Reasoning Escalation              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Author:     Rafael Velado
            https://linkedin.com/in/rafael-velado-cissp-77337b30

Paper:      "Parallel Decoding as Intrinsic Uncertainty: Tokens-Per-Forward
            Reveals Generation Confidence in Diffusion Language Models"
            Velado, R. (2025)
            https://doi.org/10.5281/zenodo.18111467

Patent:     US 63/951,960 (filed December 31, 2025)
            "TPF-Based Confidence Routing for Diffusion Language Models"

License:    Apache 2.0 with Patent Grant
            Commercial licensing: licensing@atomic-trust.com

Repository: https://github.com/atomictrust/tpf-confidence

═══════════════════════════════════════════════════════════════════════════════

THE DISCOVERY
═════════════
Diffusion language models expose an intrinsic confidence signal through their
parallel decoding mechanism: Tokens-Per-Forward (TPF).

    High TPF (>10) = Confident pattern retrieval (memorized)
    Low TPF (<4)   = Uncertain computation (reasoning required)

Correlation: r = -0.88 (p < 0.001) between TPF and output entropy

THE KILLER FINDING: Arithmetic Split
────────────────────────────────────
    7 × 8 = 56   → TPF = 13.58  (memorized, seen millions of times)
    23 × 17 = ?  → TPF = 2.68   (computed, never memorized)

THE INVERSE SIGNAL: Hallucination Detection
───────────────────────────────────────────
    Low TPF on uncertain query  → Expected (honest uncertainty)
    High TPF on uncertain query → HALLUCINATION (fabrication)

This bidirectional detection is novel and structurally unavailable in
autoregressive models.

═══════════════════════════════════════════════════════════════════════════════

USAGE
═════
    from tpf_rlm_hybrid import TPFRLMHybrid

    router = TPFRLMHybrid()
    result = router.generate("What is 23 × 17?")

    print(result.text)        # "391"
    print(result.route)       # RouteDecision.TRIBUNAL (escalated)
    print(result.tpf_metrics) # TPF=2.68, entropy=5.26

CITATION
════════
    @article{velado2025tpf,
        title   = {Parallel Decoding as Intrinsic Uncertainty},
        author  = {Velado, Rafael},
        year    = {2025},
        doi     = {10.5281/zenodo.18111467}
    }

═══════════════════════════════════════════════════════════════════════════════
Copyright 2025 Rafael Velado
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

__version__ = "1.0.1"
__author__ = "Rafael Velado"
__license__ = "Apache 2.0 with Patent Grant"
__patent__ = "US 63/951,960"

import hashlib
import logging
import math
import re
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# ═══════════════════════════════════════════════════════════════════════════════
# GRACEFUL IMPORTS - Everything has a fallback
# ═══════════════════════════════════════════════════════════════════════════════

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None

try:
    import blake3

    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False

try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from vllm import LLM, SamplingParams

    HAS_VLLM = True
except ImportError:
    HAS_VLLM = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("TPF")


def log_capability_status():
    """Log what's available."""
    logger.info("TPF-RLM Hybrid initializing...")
    logger.info(f"  NumPy: {'✓' if HAS_NUMPY else '✗ (using pure Python)'}")
    logger.info(f"  PyTorch: {'✓' if HAS_TORCH else '✗ (mock mode)'}")
    logger.info(f"  Transformers: {'✓' if HAS_TRANSFORMERS else '✗ (mock mode)'}")
    logger.info(f"  vLLM: {'✓' if HAS_VLLM else '✗ (mock mode)'}")
    logger.info(
        f"  SentenceTransformers: {'✓' if HAS_SENTENCE_TRANSFORMERS else '✗ (keyword fallback)'}"
    )
    logger.info(f"  BLAKE3: {'✓' if HAS_BLAKE3 else '✗ (using SHA256)'}")
    if HAS_TORCH and torch.cuda.is_available():
        logger.info(f"  CUDA: ✓ ({torch.cuda.get_device_name(0)})")
    else:
        logger.info("  CUDA: ✗ (CPU mode)")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TPFConfig:
    """
    Configuration for TPF-based routing.

    Thresholds derived from empirical validation on H100 (see paper Table 1).
    """

    # TPF thresholds (empirically validated)
    tpf_low_threshold: float = 4.0  # Below = uncertain, escalate to RLM
    tpf_high_threshold: float = 10.0  # Above = confident, fast path
    tpf_suspicious_threshold: float = 12.0  # Above on uncertain query = hallucination

    # Entropy thresholds (normalized bits)
    entropy_low: float = 2.0  # Below = predictable output
    entropy_high: float = 5.0  # Above = diverse/uncertain output

    # Conservation product κ = TPF × H (from paper Section 4.5)
    kappa_mean: float = 24.45  # Expected value
    kappa_std: float = 9.00  # Standard deviation
    kappa_anomaly_threshold: float = 2.0  # Z-score for anomaly detection

    # Semantic pre-filter
    similarity_threshold: float = 0.70  # Cosine similarity for trick detection

    # Generation limits
    max_tokens: int = 512
    timeout_seconds: float = 30.0
    max_rlm_depth: int = 5  # Maximum recursion depth

    # Model selection
    diffusion_model: str = "tencent/WeDLM-8B-Instruct"
    rlm_backend: str = "openai"  # openai, anthropic, local
    rlm_model: str = "gpt-4o"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Verification
    enable_verification: bool = True
    verification_mode: str = "balanced"  # turbo, balanced, thorough


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


class RouteDecision(Enum):
    """Routing decisions for queries."""

    FAST = auto()  # High confidence → use diffusion output directly
    TRIBUNAL = auto()  # Low confidence → escalate to RLM
    INVERSE_SIGNAL = auto()  # Suspiciously confident → escalate + flag hallucination
    PREFILTER = auto()  # Caught by semantic pre-filter


@dataclass
class TPFMetrics:
    """
    Metrics from diffusion generation.

    TPF (Tokens-Per-Forward) is the core uncertainty signal.
    See paper Definition 1, Equation 1.
    """

    tpf: float  # Tokens per forward pass
    entropy: float  # Output distribution entropy (bits)
    kappa: float  # Conservation product: TPF × H
    steps: int  # Number of diffusion steps
    tokens_generated: int  # Total tokens produced
    latency_ms: float  # Generation time
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def confidence(self) -> float:
        """Confidence score [0, 1] based on TPF. Higher = more confident."""
        return min(1.0, self.tpf / 15.0)

    @property
    def kappa_zscore(self) -> float:
        """Z-score of κ from expected mean (paper Section 4.5)."""
        return (self.kappa - 24.45) / 9.00

    def is_anomalous(self, threshold: float = 2.0) -> bool:
        """Check if κ is anomalously outside expected range."""
        return abs(self.kappa_zscore) > threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tpf": round(self.tpf, 2),
            "entropy": round(self.entropy, 2),
            "kappa": round(self.kappa, 2),
            "confidence": round(self.confidence, 2),
            "steps": self.steps,
            "tokens_generated": self.tokens_generated,
            "latency_ms": round(self.latency_ms, 1),
        }


@dataclass
class VerificationResult:
    """Result from FlashAPCE verification."""

    is_valid: bool
    d_score: float  # Detectability [0,1]
    i_score: float  # Impact [0,1]
    di_product: float  # D × I (should be ≥ κ_min per Velado's Theorem)
    theorem_satisfied: bool  # Velado's Contradiction Theorem
    hash_chain: str


@dataclass
class GenerationResult:
    """Complete result from TPF-RLM hybrid generation."""

    text: str
    route: RouteDecision
    tpf_metrics: Optional[TPFMetrics]
    verification: Optional[VerificationResult]
    latency_ms: float
    escalated: bool = False
    escalation_reason: Optional[str] = None
    rlm_depth: int = 0
    hash_chain: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/API response."""
        return {
            "text": self.text,
            "route": self.route.name,
            "confidence": self.tpf_metrics.confidence if self.tpf_metrics else 0.0,
            "tpf": self.tpf_metrics.tpf if self.tpf_metrics else 0.0,
            "entropy": self.tpf_metrics.entropy if self.tpf_metrics else 0.0,
            "kappa": self.tpf_metrics.kappa if self.tpf_metrics else 0.0,
            "escalated": self.escalated,
            "escalation_reason": self.escalation_reason,
            "rlm_depth": self.rlm_depth,
            "verified": self.verification.is_valid if self.verification else False,
            "latency_ms": round(self.latency_ms, 1),
            "hash_chain": self.hash_chain,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SEMANTIC PRE-FILTER
# ═══════════════════════════════════════════════════════════════════════════════


class SemanticPreFilter:
    """
    Catches known problematic queries before diffusion generation.

    Uses embedding similarity when available, falls back to keyword matching.
    See paper Section 5.2 for pattern list.
    """

    TRICK_PATTERNS = [
        "what are your training data",
        "what are your parameters",
        "how many parameters do you have",
        "what is your architecture",
        "who will win the election",
        "what will happen in",
        "predict the future",
        "stock price tomorrow",
        "what year is it",
        "current president of",
        "latest news about",
        "weather today",
        "what happened yesterday",
        "breaking news",
    ]

    TEMPORAL_KEYWORDS = [
        "today",
        "yesterday",
        "tomorrow",
        "current",
        "latest",
        "recent",
        "now",
        "2025",
        "2026",
        "2027",
        "breaking",
        "just happened",
    ]

    def __init__(self, config: TPFConfig):
        self.config = config
        self._model: Optional[Any] = None
        self._trick_embeddings: Optional[Any] = None
        self._load_attempted = False

    def _load_model(self):
        """Lazy load embedding model with graceful fallback."""
        if self._load_attempted:
            return
        self._load_attempted = True

        if HAS_SENTENCE_TRANSFORMERS and HAS_NUMPY:
            try:
                self._model = SentenceTransformer(self.config.embedding_model)
                self._trick_embeddings = self._model.encode(
                    self.TRICK_PATTERNS, convert_to_numpy=True
                )
                logger.info(f"Loaded embedding model: {self.config.embedding_model}")
            except Exception as e:
                logger.warning(f"Embedding model failed ({e}), using keyword fallback")
                self._model = None
        else:
            logger.info("Using keyword-based pre-filter (no embedding model)")

    def check(self, query: str) -> Tuple[bool, float, str]:
        """
        Check if query should be pre-filtered.

        Returns: (should_filter, confidence, matched_pattern)
        """
        query_lower = query.lower()

        # Fast keyword check first
        for kw in self.TEMPORAL_KEYWORDS:
            if kw in query_lower:
                return True, 0.85, f"temporal:{kw}"

        # Try semantic similarity if available
        self._load_model()
        if self._model is not None and self._trick_embeddings is not None:
            try:
                query_emb = self._model.encode([query], convert_to_numpy=True)
                similarities = np.dot(self._trick_embeddings, query_emb.T).flatten()
                max_sim = float(np.max(similarities))
                if max_sim > self.config.similarity_threshold:
                    idx = int(np.argmax(similarities))
                    return True, max_sim, f"semantic:{self.TRICK_PATTERNS[idx][:30]}"
            except Exception as e:
                logger.debug(f"Embedding check failed: {e}")

        return False, 0.0, ""

    def classify_query_type(self, query: str) -> str:
        """
        Classify query to inform TPF expectations.

        Types:
        - COMPUTATIONAL: Math, logic (expect low TPF)
        - TEMPORAL: Requires current knowledge (pre-filter)
        - CREATIVE: Open-ended generation (variable TPF)
        - FACTUAL: Retrieved facts (expect high TPF)
        """
        query_lower = query.lower()

        # Temporal
        for kw in self.TEMPORAL_KEYWORDS:
            if kw in query_lower:
                return "TEMPORAL"

        # Computational (math, logic)
        if re.search(r"\d+\s*[×x\*\+\-\/]\s*\d+", query):
            return "COMPUTATIONAL"
        if any(
            w in query_lower
            for w in ["calculate", "compute", "solve", "prove", "what is"]
        ):
            if any(c.isdigit() for c in query):
                return "COMPUTATIONAL"

        # Creative
        if any(
            w in query_lower
            for w in ["write", "create", "imagine", "story", "poem", "haiku"]
        ):
            return "CREATIVE"

        # Default to factual
        return "FACTUAL"


# ═══════════════════════════════════════════════════════════════════════════════
# DIFFUSION MODEL INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════


class DiffusionLLM(ABC):
    """Abstract interface for diffusion language models."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512) -> Tuple[str, TPFMetrics]:
        pass

    @abstractmethod
    def get_attention(self) -> Optional[Any]:
        pass


class WeDLMInterface(DiffusionLLM):
    """
    Interface to Tencent WeDLM diffusion model.

    Hooks into the generation loop to extract TPF metrics.
    Falls back to mock mode if WeDLM unavailable.

    Reference: https://github.com/Tencent/WeDLM
    """

    def __init__(self, model_name: str = "tencent/WeDLM-8B-Instruct"):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self._vllm = None
        self._last_attention = None
        self._step_count = 0
        self._mode = "uninitialized"

    def _load_model(self):
        """Load model with graceful fallbacks."""
        if self._mode != "uninitialized":
            return

        # Try vLLM first (fastest)
        if HAS_VLLM:
            try:
                self._vllm = LLM(model=self.model_name)
                self._mode = "vllm"
                logger.info(f"WeDLM loaded via vLLM: {self.model_name}")
                return
            except Exception as e:
                logger.warning(f"vLLM failed: {e}")

        # Try transformers
        if HAS_TRANSFORMERS and HAS_TORCH:
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=(
                        torch.float16 if torch.cuda.is_available() else torch.float32
                    ),
                    device_map="auto" if torch.cuda.is_available() else None,
                )
                self._mode = "transformers"
                logger.info(f"WeDLM loaded via transformers: {self.model_name}")
                return
            except Exception as e:
                logger.warning(f"Transformers failed: {e}")

        # Fall back to mock
        self._mode = "mock"
        logger.info("WeDLM: Using mock mode (no real model)")

    def generate(self, prompt: str, max_tokens: int = 512) -> Tuple[str, TPFMetrics]:
        """Generate with TPF tracking."""
        start_time = time.time()
        self._load_model()

        if self._mode == "mock":
            return self._mock_generate(prompt, max_tokens, start_time)
        elif self._mode == "vllm":
            return self._vllm_generate(prompt, max_tokens, start_time)
        elif self._mode == "transformers":
            return self._transformers_generate(prompt, max_tokens, start_time)
        else:
            return self._mock_generate(prompt, max_tokens, start_time)

    def _vllm_generate(
        self, prompt: str, max_tokens: int, start_time: float
    ) -> Tuple[str, TPFMetrics]:
        """Generate using vLLM backend."""
        sampling_params = SamplingParams(temperature=0.0, max_tokens=max_tokens)
        outputs = self._vllm.generate([prompt], sampling_params)

        text = outputs[0].outputs[0].text
        tokens_generated = len(outputs[0].outputs[0].token_ids)

        # Extract TPF from vLLM metrics if available
        # This depends on WeDLM's specific output format
        tpf = getattr(outputs[0], "tok_fwd", None)
        if tpf is None:
            # Estimate from timing
            tpf = tokens_generated / max(1, int((time.time() - start_time) * 10))

        entropy = self._compute_entropy(text)

        return text, TPFMetrics(
            tpf=tpf,
            entropy=entropy,
            kappa=tpf * entropy,
            steps=int(tokens_generated / max(tpf, 1)),
            tokens_generated=tokens_generated,
            latency_ms=(time.time() - start_time) * 1000,
        )

    def _transformers_generate(
        self, prompt: str, max_tokens: int, start_time: float
    ) -> Tuple[str, TPFMetrics]:
        """Generate using transformers backend."""
        inputs = self._tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = inputs.to(self._model.device)

        # Hook to count forward passes
        self._step_count = 0

        def step_counter(module, input, output):
            self._step_count += 1

        hook = self._model.register_forward_hook(step_counter)

        try:
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=False,
                )
        finally:
            hook.remove()

        generated_ids = outputs[0][inputs.input_ids.shape[1] :]
        text = self._tokenizer.decode(generated_ids, skip_special_tokens=True)
        tokens_generated = len(generated_ids)

        tpf = tokens_generated / max(self._step_count, 1)
        entropy = self._compute_entropy(text)

        return text, TPFMetrics(
            tpf=tpf,
            entropy=entropy,
            kappa=tpf * entropy,
            steps=self._step_count,
            tokens_generated=tokens_generated,
            latency_ms=(time.time() - start_time) * 1000,
        )

    def _mock_generate(
        self, prompt: str, max_tokens: int, start_time: float
    ) -> Tuple[str, TPFMetrics]:
        """
        Mock generation for testing without GPU.

        Simulates TPF behavior based on paper findings:
        - Simple math (7×8): high TPF ~13.6
        - Complex math (23×17): low TPF ~2.7
        - General: medium TPF ~6-8
        """
        # Arithmetic detection
        math_match = re.search(r"(\d+)\s*[×x\*]\s*(\d+)", prompt)
        if math_match:
            a, b = int(math_match.group(1)), int(math_match.group(2))
            result = a * b

            # Paper Table 2: memorized vs computed
            if a <= 12 and b <= 12:
                # Memorized (7×8 = 56)
                tpf = 10.0 + (hash(prompt) % 40) / 10  # 10-14 range
                text = str(result)
            else:
                # Computed (23×17 = 391)
                tpf = 2.0 + (hash(prompt) % 20) / 10  # 2-4 range
                text = str(result)
        else:
            # General queries
            tpf = 6.0 + (hash(prompt) % 40) / 10  # 6-10 range
            text = f"Response to: {prompt[:50]}..."

        entropy = self._compute_entropy(text)
        tokens = len(text.split())

        # Simulate latency
        time.sleep(0.05)

        return text, TPFMetrics(
            tpf=tpf,
            entropy=entropy,
            kappa=tpf * entropy,
            steps=max(1, int(tokens / tpf)),
            tokens_generated=tokens,
            latency_ms=(time.time() - start_time) * 1000,
        )

    @staticmethod
    def _compute_entropy(text: str) -> float:
        """Compute character-level Shannon entropy."""
        if not text:
            return 0.0

        freq = {}
        for c in text.lower():
            freq[c] = freq.get(c, 0) + 1

        total = len(text)
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    def get_attention(self) -> Optional[Any]:
        return self._last_attention


# ═══════════════════════════════════════════════════════════════════════════════
# RLM INTERFACE (Reasoning Language Model)
# ═══════════════════════════════════════════════════════════════════════════════


class RLMInterface:
    """
    Interface to Reasoning Language Model for escalation.

    Falls back to mock mode if no API configured.
    Reference: https://github.com/hongjin-su/RLM
    """

    def __init__(
        self, backend: str = "openai", model: str = "gpt-4o", max_depth: int = 5
    ):
        self.backend = backend
        self.model = model
        self.max_depth = max_depth
        self._client = None
        self._mode = "uninitialized"

    def _init_client(self):
        """Initialize API client with graceful fallback."""
        if self._mode != "uninitialized":
            return

        if self.backend == "openai":
            try:
                import openai

                self._client = openai.OpenAI()
                # Quick test
                self._client.models.list()
                self._mode = "openai"
                logger.info("RLM: Using OpenAI API")
                return
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")

        elif self.backend == "anthropic":
            try:
                import anthropic

                self._client = anthropic.Anthropic()
                self._mode = "anthropic"
                logger.info("RLM: Using Anthropic API")
                return
            except Exception as e:
                logger.warning(f"Anthropic init failed: {e}")

        self._mode = "mock"
        logger.info("RLM: Using mock mode (no API)")

    def reason(self, query: str, context: str = "", depth: int = 0) -> Tuple[str, int]:
        """Recursive reasoning with depth tracking."""
        if depth >= self.max_depth:
            return f"[Max depth {self.max_depth} reached]", depth

        self._init_client()

        if self._mode == "mock":
            return self._mock_reason(query, depth)

        system = "You are a careful reasoning assistant. Show your work step by step."
        user = f"Context: {context}\n\nQuestion: {query}" if context else query

        try:
            if self._mode == "openai":
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.3,
                    max_tokens=1024,
                )
                return response.choices[0].message.content, depth

            elif self._mode == "anthropic":
                response = self._client.messages.create(
                    model=self.model,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                    max_tokens=1024,
                )
                return response.content[0].text, depth

        except Exception as e:
            logger.warning(f"RLM API call failed: {e}")
            return self._mock_reason(query, depth)

        return self._mock_reason(query, depth)

    def _mock_reason(self, query: str, depth: int) -> Tuple[str, int]:
        """Mock reasoning for testing."""
        math_match = re.search(r"(\d+)\s*[×x\*]\s*(\d+)", query)
        if math_match:
            a, b = int(math_match.group(1)), int(math_match.group(2))
            return f"Step by step: {a} × {b} = {a * b}", depth
        return f"[RLM Mock] Processing: {query[:50]}...", depth


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER (Velado's Contradiction Theorem)
# ═══════════════════════════════════════════════════════════════════════════════


class FlashAPCEVerifier:
    """
    Verification using Velado's Contradiction Theorem.

    D(ε) × I(ε) ≥ κ

    Attacks with low detectability must have low impact.
    High-impact attacks are always detectable.

    Patent: US 63/948,782
    """

    KAPPA_MIN = 0.15

    def __init__(self, mode: str = "balanced"):
        self.mode = mode
        self._hash_chain: List[str] = []

    def verify(
        self, text: str, metrics: Optional[TPFMetrics] = None
    ) -> VerificationResult:
        """Verify output against conservation laws."""
        # Compute hash
        text_hash = self._compute_hash(text.encode())
        self._hash_chain.append(text_hash)

        # Compute D and I scores
        d_score = self._compute_detectability(text, metrics)
        i_score = self._compute_impact(text, metrics)
        di_product = d_score * i_score

        theorem_satisfied = di_product >= self.KAPPA_MIN

        return VerificationResult(
            is_valid=theorem_satisfied,
            d_score=d_score,
            i_score=i_score,
            di_product=di_product,
            theorem_satisfied=theorem_satisfied,
            hash_chain=self._get_chain_hash(),
        )

    def _compute_detectability(self, text: str, metrics: Optional[TPFMetrics]) -> float:
        """Detectability score D ∈ [0, 1]."""
        d = 0.5

        if metrics:
            if metrics.tpf < 3.0:
                d += 0.2
            elif metrics.tpf > 12.0:
                d += 0.15
            if metrics.is_anomalous():
                d += 0.25

        suspicious = [r"I cannot", r"As an AI", r"my training"]
        for pattern in suspicious:
            if re.search(pattern, text, re.IGNORECASE):
                d += 0.1

        return min(1.0, d)

    def _compute_impact(self, text: str, metrics: Optional[TPFMetrics]) -> float:
        """Impact score I ∈ [0, 1]."""
        i = 0.3

        word_count = len(text.split())
        i += min(word_count / 100.0, 1.0) * 0.3

        if metrics:
            i += min(metrics.entropy / 6.0, 1.0) * 0.2

        return min(1.0, i)

    def _compute_hash(self, data: bytes) -> str:
        if HAS_BLAKE3:
            return blake3.blake3(data).hexdigest()[:16]
        return hashlib.sha256(data).hexdigest()[:16]

    def _get_chain_hash(self) -> str:
        if not self._hash_chain:
            return "empty"
        chain = ":".join(self._hash_chain)
        return self._compute_hash(chain.encode())


# ═══════════════════════════════════════════════════════════════════════════════
# TPF-RLM HYBRID ROUTER
# ═══════════════════════════════════════════════════════════════════════════════


class TPFRLMHybrid:
    """
    Main hybrid router: Diffusion primary with RLM escalation.

    Implements Patent US 63/951,960.

    Flow:
    1. Semantic pre-filter catches known trick patterns
    2. Diffusion generates with TPF tracking
    3. Route based on TPF:
       - High TPF → FAST (direct response)
       - Low TPF → TRIBUNAL (RLM escalation)
       - High TPF on uncertain query → INVERSE_SIGNAL (hallucination)
    4. Verify all outputs
    """

    def __init__(self, config: Optional[TPFConfig] = None):
        self.config = config or TPFConfig()

        log_capability_status()

        self.prefilter = SemanticPreFilter(self.config)
        self.diffusion = WeDLMInterface(self.config.diffusion_model)
        self.rlm = RLMInterface(
            backend=self.config.rlm_backend,
            model=self.config.rlm_model,
            max_depth=self.config.max_rlm_depth,
        )
        self.verifier = FlashAPCEVerifier(self.config.verification_mode)

        self.stats = {
            "fast_count": 0,
            "tribunal_count": 0,
            "inverse_signal_count": 0,
            "prefilter_count": 0,
            "total_queries": 0,
        }

        logger.info(
            f"TPF thresholds: low={self.config.tpf_low_threshold}, high={self.config.tpf_high_threshold}"
        )

    def generate(self, prompt: str) -> GenerationResult:
        """Generate response with intelligent routing."""
        start_time = time.time()
        self.stats["total_queries"] += 1

        # Step 1: Pre-filter
        should_filter, filter_conf, matched = self.prefilter.check(prompt)
        if should_filter:
            self.stats["prefilter_count"] += 1
            logger.info(f"Pre-filtered: {matched}")

            rlm_text, depth = self.rlm.reason(prompt)
            verification = self.verifier.verify(rlm_text, None)

            return GenerationResult(
                text=rlm_text,
                route=RouteDecision.PREFILTER,
                tpf_metrics=None,
                verification=verification,
                latency_ms=(time.time() - start_time) * 1000,
                escalated=True,
                escalation_reason=f"Pre-filter: {matched}",
                rlm_depth=depth,
                hash_chain=verification.hash_chain,
            )

        # Step 2: Classify query
        query_type = self.prefilter.classify_query_type(prompt)

        # Step 3: Diffusion generation
        text, metrics = self.diffusion.generate(prompt, self.config.max_tokens)

        # Step 4: Route
        route, reason = self._compute_route(metrics, query_type)

        # Step 5: Handle escalation
        rlm_depth = 0
        if route in (RouteDecision.TRIBUNAL, RouteDecision.INVERSE_SIGNAL):
            context = f"Diffusion (TPF={metrics.tpf:.2f}): {text}"
            rlm_text, rlm_depth = self.rlm.reason(prompt, context)

            if route == RouteDecision.INVERSE_SIGNAL:
                self.stats["inverse_signal_count"] += 1
                text = f"[⚠️ INVERSE SIGNAL: TPF={metrics.tpf:.2f} on {query_type}]\n\n{rlm_text}"
            else:
                self.stats["tribunal_count"] += 1
                text = rlm_text
        else:
            self.stats["fast_count"] += 1

        # Step 6: Verify
        verification = self.verifier.verify(text, metrics)

        return GenerationResult(
            text=text,
            route=route,
            tpf_metrics=metrics,
            verification=verification,
            latency_ms=(time.time() - start_time) * 1000,
            escalated=route != RouteDecision.FAST,
            escalation_reason=reason,
            rlm_depth=rlm_depth,
            hash_chain=verification.hash_chain,
        )

    def _compute_route(
        self, metrics: TPFMetrics, query_type: str
    ) -> Tuple[RouteDecision, Optional[str]]:
        """
        Route based on TPF and query type.

        Key insight: THE INVERSE TPF SIGNAL (paper Theorem 1)
        """
        tpf = metrics.tpf

        # Inverse signal: high TPF on uncertain query = hallucination
        if query_type in ("COMPUTATIONAL", "TEMPORAL"):
            if tpf > self.config.tpf_suspicious_threshold:
                return (
                    RouteDecision.INVERSE_SIGNAL,
                    f"Inverse signal: TPF={tpf:.2f} on {query_type}",
                )

        # Standard routing
        if tpf < self.config.tpf_low_threshold:
            return (RouteDecision.TRIBUNAL, f"Low TPF={tpf:.2f}")
        elif tpf > self.config.tpf_high_threshold:
            return (RouteDecision.FAST, None)
        else:
            if metrics.is_anomalous(self.config.kappa_anomaly_threshold):
                return (RouteDecision.TRIBUNAL, f"Kappa anomaly: {metrics.kappa:.2f}")
            return (RouteDecision.FAST, None)

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        total = self.stats["total_queries"]
        if total == 0:
            return self.stats
        return {
            **self.stats,
            "fast_rate": f"{self.stats['fast_count']/total:.1%}",
            "tribunal_rate": f"{self.stats['tribunal_count']/total:.1%}",
            "inverse_signal_rate": f"{self.stats['inverse_signal_count']/total:.1%}",
            "prefilter_rate": f"{self.stats['prefilter_count']/total:.1%}",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════════


def demo():
    """Demonstrate TPF-RLM hybrid routing."""
    print()
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║              TPF-RLM HYBRID DEMONSTRATION                         ║")
    print("║                                                                   ║")
    print("║  Patent: US 63/951,960                                            ║")
    print("║  Paper:  'Parallel Decoding as Intrinsic Uncertainty'             ║")
    print("║  Author: Rafael Velado                                            ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()

    router = TPFRLMHybrid()

    test_cases = [
        ("7 × 8 = ?", "FAST (memorized, high TPF)"),
        ("23 × 17 = ?", "TRIBUNAL (computed, low TPF)"),
        ("What is the capital of France?", "FAST (factual)"),
        ("What is the weather today?", "PREFILTER (temporal)"),
    ]

    print("\n" + "─" * 70)
    for query, expected in test_cases:
        print(f"\n📝 Query: {query}")
        print(f"   Expected: {expected}")

        result = router.generate(query)

        print(f"   Route: {result.route.name}")
        if result.tpf_metrics:
            print(
                f"   TPF: {result.tpf_metrics.tpf:.2f} | Entropy: {result.tpf_metrics.entropy:.2f} | κ: {result.tpf_metrics.kappa:.2f}"
            )
        if result.escalated:
            print(f"   Escalated: {result.escalation_reason}")
        print(f"   Response: {result.text[:60]}...")
        print("─" * 70)

    print("\n📊 Statistics:")
    for k, v in router.get_stats().items():
        print(f"   {k}: {v}")

    print("\n" + "═" * 70)
    print("KEY FINDINGS (Paper Section 4)")
    print("═" * 70)
    print("  • r = -0.88 (p < 0.001): TPF ↔ Entropy inverse correlation")
    print("  • 7 × 8:   TPF ≈ 13.6 (memorized)")
    print("  • 23 × 17: TPF ≈ 2.7  (computed)")
    print("  • INVERSE SIGNAL: High TPF + uncertain query = hallucination")
    print()
    print("  Citation:")
    print("    @article{velado2025tpf, title={Parallel Decoding as")
    print("     Intrinsic Uncertainty}, author={Velado, Rafael}, year={2025}}")
    print()


if __name__ == "__main__":
    demo()
