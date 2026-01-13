"""
APCE - Attention Provenance & Conservation Engine
==================================================

Runtime verification for transformer models using conservation laws.

v0.2.0: Extended 11-signal manifold for weight backdoor detection.
- Signals 1-8: Attention pathway (original APCE)
- Signals 9-10: Value pathway (magnitude variance, directional coherence)
- Signal 11: Projection pathway (residual norm)

Quick Start:
    from apce import APCEVerifier, verify, verify_extended
    from apce.wrappers import ClaudeWrapper, GPTWrapper, LlamaWrapper
    from apce.compliance import Watermarker

    # Verify attention weights directly (8-signal)
    result = verify(attention_matrix)
    print(f"Valid: {result.is_valid}")

    # Extended verification for backdoors (11-signal)
    result = verify_extended(attention_weights, value_representations)
    print(f"Backdoor-free: {result.is_valid}")
    print(f"Detection pathway: {result.violated_pathway}")

    # Wrap API models with verification
    claude = ClaudeWrapper(api_key="...")
    response = claude.chat([{"role": "user", "content": "Hello"}])
    print(response.provenance.merkle_root)

    # Full verification with local models
    llama = LlamaWrapper(model_name="meta-llama/Llama-2-7b-chat-hf")
    result = llama.chat([{"role": "user", "content": "Hello"}])
    print(f"Conservation valid: {result.analysis.is_valid}")

    # EU AI Act watermarking
    wm = Watermarker(model_id="gpt-4")
    marked = wm.watermark_text("AI response...")

License: Apache 2.0
Author: Rafael Velado (raf@atomic-trust.com)
Website: https://atomic-trust.com
"""

__version__ = "0.2.2"
__author__ = "Rafael Velado"
__email__ = "raf@atomic-trust.com"

from .core import (
    # Main classes
    APCEVerifier,
    VerificationMode,
    ManifoldAnalysis,
    ExtendedManifoldAnalysis,  # v0.2.0: 11-signal manifold
    ProvenanceBundle,
    ConservationSignal,
    SecurityViolation,
    BackdoorDetected,  # v0.2.0: Weight backdoor exception

    # Convenience functions
    verify,
    verify_extended,  # v0.2.0: 11-signal verification
    is_valid,
    is_backdoor_free,  # v0.2.0: Weight backdoor check
    compute_hash,
    
    # Baseline calibration (v0.2.2)
    calibrate_baseline,
    reset_baseline,
    get_shared_verifier,

    # Constants
    KAPPA,
    KAPPA_B,  # v0.2.0: Extended security constant
    DETECTION_THRESHOLD,
)

# Wrapper base (for subclassing)
from .wrappers.base import APCEWrapper, VerifiedResponse

__all__ = [
    # Version
    "__version__",

    # Core verification (8-signal)
    "APCEVerifier",
    "VerificationMode",
    "ManifoldAnalysis",
    "ProvenanceBundle",
    "ConservationSignal",
    "SecurityViolation",

    # Extended verification (11-signal) - v0.2.0
    "ExtendedManifoldAnalysis",
    "BackdoorDetected",

    # Base wrapper
    "APCEWrapper",
    "VerifiedResponse",

    # Functions (8-signal)
    "verify",
    "is_valid",
    "compute_hash",

    # Functions (11-signal) - v0.2.0
    "verify_extended",
    "is_backdoor_free",
    
    # Baseline calibration - v0.2.2
    "calibrate_baseline",
    "reset_baseline",
    "get_shared_verifier",

    # Constants
    "KAPPA",
    "KAPPA_B",  # v0.2.0
    "DETECTION_THRESHOLD",
]
