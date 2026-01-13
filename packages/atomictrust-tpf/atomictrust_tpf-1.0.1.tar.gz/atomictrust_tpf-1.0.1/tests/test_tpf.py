"""
Tests for atomictrust-tpf package.

Run with: pytest tests/ -v
"""

import sys

import pytest

# =============================================================================
# Capability Detection
# =============================================================================


def has_torch():
    try:
        import torch

        return True
    except ImportError:
        return False


def has_cuda():
    if has_torch():
        import torch

        return torch.cuda.is_available()
    return False


def has_triton():
    try:
        import triton

        return True
    except ImportError:
        return False


def has_numpy():
    try:
        import numpy

        return True
    except ImportError:
        return False


# =============================================================================
# Import Tests
# =============================================================================


class TestImports:
    """Test that package imports work correctly."""

    def test_package_imports(self):
        """Package must import without errors."""
        from atomictrust_tpf import (
            FlashAPCEAttention,
            TPFConfig,
            TPFRLMHybrid,
            VerificationMode,
            __version__,
        )

        assert __version__ == "1.0.0"

    def test_router_imports(self):
        """Router module must import."""
        from atomictrust_tpf.router import (
            GenerationResult,
            RouteDecision,
            TPFConfig,
            TPFMetrics,
            TPFRLMHybrid,
        )

        assert TPFConfig is not None

    def test_flashapce_imports(self):
        """FlashAPCE module must import."""
        from atomictrust_tpf.flashapce import (
            APCESignals,
            FlashAPCEAttention,
            VerificationMode,
            verify_attention,
        )

        assert FlashAPCEAttention is not None


# =============================================================================
# Configuration Tests
# =============================================================================


class TestConfig:
    """Test configuration defaults."""

    def test_tpf_config_defaults(self):
        """Config defaults must be valid."""
        from atomictrust_tpf import TPFConfig

        config = TPFConfig()
        assert config.tpf_low_threshold < config.tpf_high_threshold
        assert config.kappa_mean > 0
        assert config.max_tokens > 0

    def test_verification_modes(self):
        """All verification modes must exist."""
        from atomictrust_tpf import VerificationMode

        assert VerificationMode.TURBO is not None
        assert VerificationMode.BALANCED is not None
        assert VerificationMode.THOROUGH is not None
        assert VerificationMode.FULL is not None


# =============================================================================
# Router Tests
# =============================================================================


class TestRouter:
    """Test TPF router functionality."""

    def test_router_initializes(self):
        """Router must initialize without GPU."""
        from atomictrust_tpf import TPFRLMHybrid

        router = TPFRLMHybrid()
        assert router is not None

    def test_mock_generation(self):
        """Router must generate in mock mode."""
        from atomictrust_tpf import TPFRLMHybrid

        router = TPFRLMHybrid()
        result = router.generate("What is 7 * 8?")
        assert result.text is not None
        assert len(result.text) > 0

    def test_tpf_metrics_returned(self):
        """Router must return TPF metrics."""
        from atomictrust_tpf import TPFRLMHybrid

        router = TPFRLMHybrid()
        result = router.generate("What is 7 * 8?")
        assert result.tpf_metrics is not None
        assert result.tpf_metrics.tpf > 0

    def test_prefilter_catches_temporal(self):
        """Pre-filter must catch temporal queries."""
        from atomictrust_tpf.router import SemanticPreFilter, TPFConfig

        pf = SemanticPreFilter(TPFConfig())
        caught, conf, matched = pf.check("What is the weather today?")
        assert caught is True
        assert "temporal" in matched

    def test_prefilter_allows_math(self):
        """Pre-filter must allow math queries."""
        from atomictrust_tpf.router import SemanticPreFilter, TPFConfig

        pf = SemanticPreFilter(TPFConfig())
        caught, _, _ = pf.check("What is 23 * 17?")
        assert caught is False


# =============================================================================
# FlashAPCE Tests
# =============================================================================


class TestFlashAPCE:
    """Test FlashAPCE attention verification."""

    def test_flashapce_initializes(self):
        """FlashAPCE must initialize."""
        from atomictrust_tpf import FlashAPCEAttention, VerificationMode

        attn = FlashAPCEAttention(mode=VerificationMode.BALANCED)
        assert attn is not None

    @pytest.mark.skipif(not has_numpy(), reason="NumPy not available")
    def test_numpy_forward(self):
        """FlashAPCE must work with NumPy."""
        import numpy as np

        from atomictrust_tpf import FlashAPCEAttention, VerificationMode

        attn = FlashAPCEAttention(mode=VerificationMode.FULL)

        q = np.random.randn(2, 4, 32, 32).astype(np.float32)
        k = np.random.randn(2, 4, 32, 32).astype(np.float32)
        v = np.random.randn(2, 4, 32, 32).astype(np.float32)

        output, signals = attn.forward(q, k, v)
        assert output is not None
        assert signals is not None

    @pytest.mark.skipif(not has_torch(), reason="PyTorch not available")
    def test_torch_forward(self):
        """FlashAPCE must work with PyTorch CPU tensors."""
        import torch

        from atomictrust_tpf import FlashAPCEAttention, VerificationMode

        attn = FlashAPCEAttention(mode=VerificationMode.BALANCED)

        q = torch.randn(2, 4, 32, 32)
        k = torch.randn(2, 4, 32, 32)
        v = torch.randn(2, 4, 32, 32)

        output, signals = attn.forward(q, k, v)
        assert output is not None
        assert output.shape == q.shape

    @pytest.mark.skipif(
        not has_cuda() or not has_triton(), reason="CUDA/Triton not available"
    )
    def test_triton_forward(self):
        """FlashAPCE Triton kernel must work on GPU."""
        import torch

        from atomictrust_tpf import FlashAPCEAttention, VerificationMode

        attn = FlashAPCEAttention(mode=VerificationMode.BALANCED)

        q = torch.randn(2, 8, 64, 64, device="cuda", dtype=torch.float16)
        k = torch.randn(2, 8, 64, 64, device="cuda", dtype=torch.float16)
        v = torch.randn(2, 8, 64, 64, device="cuda", dtype=torch.float16)

        output, signals = attn.forward(q, k, v)
        assert output is not None
        assert output.shape == q.shape

    @pytest.mark.skipif(not has_numpy(), reason="NumPy not available")
    def test_conservation_check(self):
        """Conservation deviation must be small for valid attention."""
        import numpy as np

        from atomictrust_tpf import FlashAPCEAttention, VerificationMode

        attn = FlashAPCEAttention(mode=VerificationMode.FULL)

        q = np.random.randn(2, 4, 32, 32).astype(np.float32)
        k = np.random.randn(2, 4, 32, 32).astype(np.float32)
        v = np.random.randn(2, 4, 32, 32).astype(np.float32)

        _, signals = attn.forward(q, k, v)
        assert signals.conservation_deviation.value < 0.01

    @pytest.mark.skipif(not has_numpy(), reason="NumPy not available")
    def test_velado_theorem(self):
        """D × I must satisfy Velado's theorem."""
        import numpy as np

        from atomictrust_tpf import KAPPA_MIN, FlashAPCEAttention, VerificationMode

        attn = FlashAPCEAttention(mode=VerificationMode.FULL)

        q = np.random.randn(2, 4, 32, 32).astype(np.float32)
        k = np.random.randn(2, 4, 32, 32).astype(np.float32)
        v = np.random.randn(2, 4, 32, 32).astype(np.float32)

        _, signals = attn.forward(q, k, v)
        result = attn.verify(signals)
        assert result.di_product >= KAPPA_MIN


# =============================================================================
# Paper Reproduction Tests
# =============================================================================


class TestPaperReproduction:
    """Test paper findings reproduction."""

    def test_memorized_vs_computed_math(self):
        """7 × 8 should have higher TPF than 23 × 17."""
        from atomictrust_tpf import TPFRLMHybrid

        router = TPFRLMHybrid()

        result_simple = router.generate("What is 7 * 8?")
        result_complex = router.generate("What is 23 * 17?")

        assert result_simple.tpf_metrics is not None
        assert result_complex.tpf_metrics is not None
        assert result_simple.tpf_metrics.tpf > result_complex.tpf_metrics.tpf


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests."""

    def test_full_pipeline(self):
        """Full pipeline: Router → FlashAPCE verification."""
        from atomictrust_tpf import TPFRLMHybrid

        router = TPFRLMHybrid()
        result = router.generate("Explain photosynthesis briefly.")

        assert result.text is not None
        assert len(result.text) > 0
        assert result.verification is not None
        assert result.hash_chain
