# PATENT COVERAGE: This file is a utility, NOT patented IP.
# This is a test/benchmark/harness file for validation purposes.
"""
Tests for APCE Core Verification
"""

import pytest
import numpy as np
from apce.core import (
    APCEVerifier,
    VerificationMode,
    ManifoldAnalysis,
    ConservationSignal,
    ProvenanceBundle,
    verify,
    is_valid,
    compute_hash,
    SecurityViolation,
    KAPPA,
)


class TestConservationLaw:
    """Test conservation law verification (sum to 1)."""

    def test_valid_attention_passes(self):
        """Valid softmax attention should pass."""
        # Create valid attention (rows sum to 1)
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        verifier = APCEVerifier()
        result = verifier.verify_attention(attention)

        assert result.is_valid
        assert result.conservation_deviation.value < 1e-6
        assert result.violation_count == 0

    def test_invalid_attention_fails(self):
        """Non-normalized attention should fail conservation."""
        # Create invalid attention (rows don't sum to 1)
        attention = np.random.rand(1, 8, 64, 64) * 2.0  # Sum > 1

        verifier = APCEVerifier()
        result = verifier.verify_attention(attention)

        assert not result.is_valid
        assert result.conservation_deviation.violated
        assert result.violation_count > 0

    def test_3d_input_handled(self):
        """Should handle 3D input (no batch dim)."""
        attention = np.random.rand(8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        verifier = APCEVerifier()
        result = verifier.verify_attention(attention)

        assert result.is_valid


class TestManifoldSignals:
    """Test 8 manifold signal computation."""

    def test_all_signals_present(self):
        """Should compute all 8 signals."""
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        verifier = APCEVerifier()
        result = verifier.verify_attention(attention)

        assert len(result.signals) == 8
        assert result.conservation_deviation is not None
        assert result.entropy_fingerprint is not None
        assert result.sparsity_index is not None
        assert result.top_k_checksum is not None
        assert result.geometric_curvature is not None
        assert result.layer_hash is not None
        assert result.numerical_stability is not None
        assert result.temporal_consistency is not None

    def test_entropy_computed(self):
        """Entropy should be non-negative."""
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        verifier = APCEVerifier()
        result = verifier.verify_attention(attention)

        assert result.entropy_fingerprint.value >= 0

    def test_numerical_stability_detects_nan(self):
        """Should detect NaN values."""
        attention = np.random.rand(1, 8, 64, 64)
        attention[0, 0, 0, 0] = np.nan

        verifier = APCEVerifier()
        result = verifier.verify_attention(attention)

        assert result.numerical_stability.violated


class TestProvenance:
    """Test cryptographic provenance generation."""

    def test_provenance_created(self):
        """Should create valid provenance bundle."""
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        verifier = APCEVerifier()
        analysis = verifier.verify_attention(attention)

        provenance = verifier.create_provenance(
            request="test request",
            response="test response",
            analysis=analysis,
            model_id="test-model"
        )

        assert isinstance(provenance, ProvenanceBundle)
        assert len(provenance.request_hash) == 64
        assert len(provenance.response_hash) == 64
        assert len(provenance.merkle_root) == 64
        assert provenance.chain_position == 1

    def test_chain_increments(self):
        """Chain position should increment."""
        verifier = APCEVerifier()
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)
        analysis = verifier.verify_attention(attention)

        p1 = verifier.create_provenance("r1", "resp1", analysis, "model")
        p2 = verifier.create_provenance("r2", "resp2", analysis, "model")

        assert p1.chain_position == 1
        assert p2.chain_position == 2
        assert p2.previous_hash == p1.merkle_root


class TestVerificationModes:
    """Test different verification modes."""

    def test_all_modes_work(self):
        """All modes should successfully verify."""
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        for mode in VerificationMode:
            verifier = APCEVerifier(mode=mode)
            result = verifier.verify_attention(attention)
            assert result.is_valid


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_verify_function(self):
        """verify() should work."""
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        result = verify(attention)
        assert isinstance(result, ManifoldAnalysis)

    def test_is_valid_function(self):
        """is_valid() should return bool."""
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        assert is_valid(attention) is True

    def test_compute_hash(self):
        """compute_hash() should return 64-char hex."""
        data = b"test data"
        h = compute_hash(data)

        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h)


class TestSecurityViolation:
    """Test SecurityViolation exception."""

    def test_exception_with_analysis(self):
        """Should include analysis in exception."""
        attention = np.random.rand(1, 8, 64, 64)
        attention = attention / attention.sum(axis=-1, keepdims=True)

        verifier = APCEVerifier()
        analysis = verifier.verify_attention(attention)

        exc = SecurityViolation("test", analysis=analysis)
        assert exc.analysis is not None


class TestKappaConstant:
    """Test Velado's Contradiction Theorem constant."""

    def test_kappa_positive(self):
        """Kappa must be positive for theorem to hold."""
        assert KAPPA > 0

    def test_kappa_reasonable(self):
        """Kappa should be in reasonable range."""
        assert 0 < KAPPA < 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
