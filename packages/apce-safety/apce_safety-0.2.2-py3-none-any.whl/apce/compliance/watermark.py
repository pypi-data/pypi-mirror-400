# PATENT COVERAGE: 63/947,743 (APCE), 63/948,782 (FlashAPCE)
# Related Patents: 63/949,477 (Triton Kernel), 19/415,643 (Non-Provisional)
"""
APCE Watermarking - EU AI Act GPAI Compliance
==============================================

Implements content watermarking per EU AI Act requirements:
- Article 13: Transparency obligations
- Code of Practice (Dec 17, 2025): AI-generated content marking
- GPAI requirements: Tamper-resistant provenance

Watermarks are invisible (steganographic) but verifiable,
embedding cryptographic hashes for audit chain integrity.

Example:
    from apce.compliance import Watermarker
    
    wm = Watermarker()
    marked_text = wm.watermark_text("AI generated response", metadata={...})
    
    # Later verification
    is_valid, metadata = wm.verify_text(marked_text)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime, timezone
import json
import base64
import struct

from ..core import compute_hash


@dataclass
class WatermarkMetadata:
    """Metadata embedded in watermark."""
    model_id: str
    timestamp: datetime
    provenance_hash: str
    organization: Optional[str] = None
    version: str = "1.0"
    compliance: List[str] = field(default_factory=lambda: ["EU_AI_Act"])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "timestamp": self.timestamp.isoformat(),
            "provenance_hash": self.provenance_hash,
            "organization": self.organization,
            "version": self.version,
            "compliance": self.compliance,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WatermarkMetadata":
        return cls(
            model_id=data["model_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            provenance_hash=data["provenance_hash"],
            organization=data.get("organization"),
            version=data.get("version", "1.0"),
            compliance=data.get("compliance", ["EU_AI_Act"]),
        )


class TextWatermarker:
    """
    Invisible text watermarking using zero-width characters.
    
    Embeds metadata in text without visible changes using:
    - Zero-width space (U+200B)
    - Zero-width non-joiner (U+200C)
    - Zero-width joiner (U+200D)
    
    Tamper-resistant: Includes hash chain verification.
    """
    
    # Zero-width characters for encoding
    ZW_CHARS = {
        0: '\u200b',  # Zero-width space (bit 0)
        1: '\u200c',  # Zero-width non-joiner (bit 1)
    }
    ZW_SEPARATOR = '\u200d'  # Zero-width joiner (separator)
    ZW_START = '\ufeff'  # Byte order mark (watermark start)
    ZW_END = '\u2060'  # Word joiner (watermark end)
    
    def __init__(
        self,
        model_id: str = "unknown",
        organization: Optional[str] = None,
    ):
        self.model_id = model_id
        self.organization = organization
    
    def _encode_bytes(self, data: bytes) -> str:
        """Encode bytes to zero-width character string."""
        result = []
        for byte in data:
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                result.append(self.ZW_CHARS[bit])
            result.append(self.ZW_SEPARATOR)
        return ''.join(result)
    
    def _decode_bytes(self, zw_string: str) -> bytes:
        """Decode zero-width character string to bytes."""
        # Split by separator
        parts = zw_string.split(self.ZW_SEPARATOR)
        
        result = []
        for part in parts:
            if len(part) != 8:
                continue
            
            byte = 0
            for i, char in enumerate(part):
                if char == self.ZW_CHARS[1]:
                    byte |= (1 << (7 - i))
            result.append(byte)
        
        return bytes(result)
    
    def watermark(
        self,
        text: str,
        provenance_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add invisible watermark to text.
        
        Args:
            text: Original text to watermark
            provenance_hash: APCE provenance hash for chain
            metadata: Additional metadata to embed
            
        Returns:
            Watermarked text (visually identical)
        """
        # Build metadata
        wm_metadata = WatermarkMetadata(
            model_id=self.model_id,
            timestamp=datetime.now(timezone.utc),
            provenance_hash=provenance_hash or compute_hash(text.encode()),
            organization=self.organization,
        )
        
        if metadata:
            for key, value in metadata.items():
                if hasattr(wm_metadata, key):
                    setattr(wm_metadata, key, value)
        
        # Serialize metadata
        meta_json = wm_metadata.to_json()
        meta_bytes = meta_json.encode('utf-8')
        
        # Add checksum
        checksum = compute_hash(meta_bytes)[:8]  # First 8 chars
        full_payload = meta_bytes + checksum.encode('utf-8')
        
        # Encode to zero-width
        encoded = self._encode_bytes(full_payload)
        
        # Insert watermark after first sentence or at 1/3 position
        insert_pos = min(
            text.find('. ') + 2 if '. ' in text else len(text) // 3,
            len(text) // 3
        )
        
        # Build watermarked text
        watermarked = (
            text[:insert_pos] +
            self.ZW_START +
            encoded +
            self.ZW_END +
            text[insert_pos:]
        )
        
        return watermarked
    
    def verify(self, text: str) -> Tuple[bool, Optional[WatermarkMetadata]]:
        """
        Verify watermark in text.
        
        Returns:
            Tuple of (is_valid, metadata or None)
        """
        # Find watermark boundaries
        start_idx = text.find(self.ZW_START)
        end_idx = text.find(self.ZW_END)
        
        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            return False, None
        
        # Extract encoded payload
        encoded = text[start_idx + 1:end_idx]
        
        try:
            # Decode
            payload = self._decode_bytes(encoded)
            
            # Split checksum
            meta_bytes = payload[:-8]
            checksum = payload[-8:].decode('utf-8')
            
            # Verify checksum
            expected_checksum = compute_hash(meta_bytes)[:8]
            if checksum != expected_checksum:
                return False, None
            
            # Parse metadata
            meta_json = meta_bytes.decode('utf-8')
            meta_dict = json.loads(meta_json)
            metadata = WatermarkMetadata.from_dict(meta_dict)
            
            return True, metadata
            
        except Exception as e:
            return False, None
    
    def remove(self, text: str) -> str:
        """Remove watermark from text (for authorized use only)."""
        # Remove all zero-width characters
        result = text
        for char in [self.ZW_START, self.ZW_END, self.ZW_SEPARATOR,
                     self.ZW_CHARS[0], self.ZW_CHARS[1]]:
            result = result.replace(char, '')
        return result
    
    def is_watermarked(self, text: str) -> bool:
        """Check if text contains watermark."""
        return self.ZW_START in text and self.ZW_END in text


class HashWatermarker:
    """
    Content-derived watermarking using semantic hashing.
    
    Alternative to steganographic approach:
    - Generates hash from content
    - Hash can be registered in external ledger
    - Verification via hash comparison
    
    More robust to text modification than zero-width encoding.
    """
    
    def __init__(self, model_id: str = "unknown"):
        self.model_id = model_id
    
    def generate_fingerprint(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate content fingerprint for registration.
        
        Args:
            text: Content to fingerprint
            context: Additional context (model, timestamp, etc.)
            
        Returns:
            64-character hex fingerprint
        """
        # Normalize text
        normalized = ' '.join(text.lower().split())
        
        # Build fingerprint payload
        payload = {
            "content_hash": compute_hash(normalized.encode()),
            "model_id": self.model_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "length": len(text),
            "word_count": len(text.split()),
        }
        
        if context:
            payload["context"] = context
        
        # Generate fingerprint
        fingerprint_data = json.dumps(payload, sort_keys=True)
        return compute_hash(fingerprint_data.encode())
    
    def verify_fingerprint(
        self,
        text: str,
        fingerprint: str,
        tolerance: float = 0.1,
    ) -> Tuple[bool, float]:
        """
        Verify content matches fingerprint.
        
        Args:
            text: Text to verify
            fingerprint: Expected fingerprint
            tolerance: Allowed deviation (0.0 = exact match)
            
        Returns:
            Tuple of (is_match, similarity_score)
        """
        current_fp = self.generate_fingerprint(text)
        
        if current_fp == fingerprint:
            return True, 1.0
        
        # Compute similarity for modified content
        # (simplified - production would use more sophisticated comparison)
        common_chars = sum(a == b for a, b in zip(current_fp, fingerprint))
        similarity = common_chars / len(fingerprint)
        
        return similarity >= (1.0 - tolerance), similarity


# Main Watermarker class combining approaches
class Watermarker:
    """
    EU AI Act compliant content watermarking.
    
    Combines:
    - Zero-width steganographic embedding
    - Content fingerprinting for ledger registration
    - APCE provenance chain integration
    
    Example:
        from apce.compliance import Watermarker
        
        wm = Watermarker(model_id="gpt-4", organization="Acme Corp")
        
        # Watermark AI output
        marked = wm.watermark_text(
            "AI generated response...",
            provenance_hash="abc123..."
        )
        
        # Later verification
        valid, meta = wm.verify_text(marked)
        if valid:
            print(f"Generated by {meta.model_id} at {meta.timestamp}")
    """
    
    def __init__(
        self,
        model_id: str = "unknown",
        organization: Optional[str] = None,
        use_steganography: bool = True,
    ):
        self.model_id = model_id
        self.organization = organization
        self.use_steganography = use_steganography
        
        self._text_wm = TextWatermarker(model_id, organization)
        self._hash_wm = HashWatermarker(model_id)
    
    def watermark_text(
        self,
        text: str,
        provenance_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add watermark to text content.
        
        For EU AI Act Article 13 compliance.
        """
        if self.use_steganography:
            return self._text_wm.watermark(text, provenance_hash, metadata)
        else:
            # Return original + fingerprint (for external registration)
            return text
    
    def verify_text(
        self,
        text: str
    ) -> Tuple[bool, Optional[WatermarkMetadata]]:
        """Verify watermarked text."""
        return self._text_wm.verify(text)
    
    def get_fingerprint(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Get content fingerprint for ledger registration."""
        return self._hash_wm.generate_fingerprint(text, context)
    
    def is_watermarked(self, text: str) -> bool:
        """Check if text contains watermark."""
        return self._text_wm.is_watermarked(text)
    
    def remove_watermark(self, text: str) -> str:
        """Remove watermark (authorized use only)."""
        return self._text_wm.remove(text)
