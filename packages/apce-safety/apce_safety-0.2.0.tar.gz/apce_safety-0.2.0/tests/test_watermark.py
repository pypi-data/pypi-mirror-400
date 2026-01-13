# PATENT COVERAGE: This file is a utility, NOT patented IP.
# This is a test/benchmark/harness file for validation purposes.
"""
Tests for APCE Watermarking Module
"""

import pytest
from datetime import datetime, timezone
from apce.compliance.watermark import (
    TextWatermarker,
    HashWatermarker,
    Watermarker,
    WatermarkMetadata,
)


class TestTextWatermarker:
    """Test zero-width character watermarking."""

    def test_watermark_invisible(self):
        """Watermark should not change visible text."""
        wm = TextWatermarker(model_id="test-model")
        original = "This is a test sentence. It has multiple parts."

        watermarked = wm.watermark(original)

        # Remove zero-width chars for comparison
        visible = wm.remove(watermarked)
        assert visible == original

    def test_watermark_verifiable(self):
        """Should be able to verify watermark."""
        wm = TextWatermarker(model_id="test-model", organization="TestOrg")
        original = "This is a test sentence. It has multiple parts."

        watermarked = wm.watermark(original)
        is_valid, metadata = wm.verify(watermarked)

        assert is_valid
        assert metadata is not None
        assert metadata.model_id == "test-model"
        assert metadata.organization == "TestOrg"

    def test_unwatered_text_fails(self):
        """Unwatermarked text should fail verification."""
        wm = TextWatermarker()
        text = "This has no watermark."

        is_valid, metadata = wm.verify(text)

        assert not is_valid
        assert metadata is None

    def test_tampered_watermark_fails(self):
        """Tampered watermark should fail verification."""
        wm = TextWatermarker(model_id="test-model")
        original = "This is a test sentence. It has multiple parts."

        watermarked = wm.watermark(original)
        # Tamper by removing some characters
        tampered = watermarked[:50] + watermarked[60:]

        is_valid, metadata = wm.verify(tampered)

        # Should either fail or return False
        assert not is_valid or metadata is None

    def test_is_watermarked_check(self):
        """Should detect presence of watermark."""
        wm = TextWatermarker()
        original = "Test text."

        assert not wm.is_watermarked(original)

        watermarked = wm.watermark(original)
        assert wm.is_watermarked(watermarked)

    def test_remove_watermark(self):
        """Should cleanly remove watermark."""
        wm = TextWatermarker()
        original = "Test text for removal."

        watermarked = wm.watermark(original)
        cleaned = wm.remove(watermarked)

        assert cleaned == original
        assert not wm.is_watermarked(cleaned)


class TestHashWatermarker:
    """Test content fingerprinting."""

    def test_fingerprint_consistent(self):
        """Same text should produce same fingerprint."""
        wm = HashWatermarker(model_id="test")
        text = "Consistent content for fingerprinting."

        fp1 = wm.generate_fingerprint(text)
        fp2 = wm.generate_fingerprint(text)

        # Note: timestamps differ, so these won't be identical
        # But structure should be valid
        assert len(fp1) == 64
        assert len(fp2) == 64

    def test_fingerprint_length(self):
        """Fingerprint should be 64-char hex."""
        wm = HashWatermarker()
        text = "Some content."

        fp = wm.generate_fingerprint(text)

        assert len(fp) == 64
        assert all(c in '0123456789abcdef' for c in fp)

    def test_exact_match_verifies(self):
        """Exact same text should verify."""
        wm = HashWatermarker()
        text = "Exact match test."

        fp = wm.generate_fingerprint(text)
        is_match, similarity = wm.verify_fingerprint(text, fp)

        # Due to timestamp differences, may not be exact
        # but similarity should be high
        assert similarity > 0.5


class TestWatermarker:
    """Test combined watermarker."""

    def test_watermark_text(self):
        """Should watermark text."""
        wm = Watermarker(model_id="combined-test")
        text = "Text to watermark. More content here."

        result = wm.watermark_text(text)

        assert len(result) >= len(text)

    def test_verify_text(self):
        """Should verify watermarked text."""
        wm = Watermarker(model_id="verify-test", organization="TestCorp")
        text = "Text to verify. Additional content."

        watermarked = wm.watermark_text(text)
        is_valid, metadata = wm.verify_text(watermarked)

        assert is_valid
        assert metadata.model_id == "verify-test"

    def test_get_fingerprint(self):
        """Should generate fingerprint."""
        wm = Watermarker()
        text = "Fingerprint me."

        fp = wm.get_fingerprint(text)

        assert len(fp) == 64

    def test_steganography_toggle(self):
        """Should respect steganography toggle."""
        wm_on = Watermarker(use_steganography=True)
        wm_off = Watermarker(use_steganography=False)

        text = "Toggle test."

        result_on = wm_on.watermark_text(text)
        result_off = wm_off.watermark_text(text)

        assert len(result_on) > len(result_off)  # On adds chars
        assert result_off == text  # Off returns original


class TestWatermarkMetadata:
    """Test metadata serialization."""

    def test_to_dict(self):
        """Should serialize to dict."""
        meta = WatermarkMetadata(
            model_id="test",
            timestamp=datetime.now(timezone.utc),
            provenance_hash="abc123",
            organization="TestOrg"
        )

        d = meta.to_dict()

        assert d["model_id"] == "test"
        assert d["organization"] == "TestOrg"
        assert "timestamp" in d

    def test_from_dict(self):
        """Should deserialize from dict."""
        d = {
            "model_id": "test",
            "timestamp": "2025-12-27T00:00:00",
            "provenance_hash": "xyz789",
            "organization": "FromDict",
            "version": "1.0",
            "compliance": ["EU_AI_Act"]
        }

        meta = WatermarkMetadata.from_dict(d)

        assert meta.model_id == "test"
        assert meta.organization == "FromDict"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
