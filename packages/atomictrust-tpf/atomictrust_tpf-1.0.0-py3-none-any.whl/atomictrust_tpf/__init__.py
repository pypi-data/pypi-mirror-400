"""
AtomicTrust TPF: Free uncertainty quantification for diffusion language models.

Author:     Rafael Velado
            https://linkedin.com/in/rafael-velado-cissp-77337b30

Paper:      "Parallel Decoding as Intrinsic Uncertainty"
            https://doi.org/10.5281/zenodo.18111467

Patent:     US 63/951,960 (filed December 31, 2025)

License:    Apache 2.0 with Patent Grant

Usage:
    from atomictrust_tpf import TPFRLMHybrid, FlashAPCEAttention

    # TPF-based routing
    router = TPFRLMHybrid()
    result = router.generate("What is 23 × 17?")
    print(f"TPF: {result.tpf_metrics.tpf}")

    # FlashAPCE verification
    attn = FlashAPCEAttention()
    output, signals = attn.forward(q, k, v)
    result = attn.verify(signals)
"""

__version__ = "1.0.0"
__author__ = "Rafael Velado"
__license__ = "Apache-2.0"
__patent__ = "US 63/951,960"

from atomictrust_tpf.flashapce import (
    KAPPA_MIN,
    APCESignals,
    FlashAPCEAttention,
    VerificationMode,
    VerificationResult,
    VerificationSignal,
    verify_attention,
)
from atomictrust_tpf.router import (
    GenerationResult,
    RouteDecision,
    TPFConfig,
    TPFMetrics,
    TPFRLMHybrid,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    "__patent__",
    # Router
    "TPFRLMHybrid",
    "TPFConfig",
    "TPFMetrics",
    "RouteDecision",
    "GenerationResult",
    # FlashAPCE
    "FlashAPCEAttention",
    "VerificationMode",
    "VerificationResult",
    "VerificationSignal",
    "APCESignals",
    "verify_attention",
    "KAPPA_MIN",
]
