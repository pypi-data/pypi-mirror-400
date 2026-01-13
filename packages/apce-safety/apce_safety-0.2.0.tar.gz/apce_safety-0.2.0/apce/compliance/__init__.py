"""
APCE Compliance - Regulatory Alignment Tools
=============================================

Tools for EU AI Act, NIST IR 8596, and ISO 42001 compliance:
- Watermarker: Content marking per EU AI Act Article 13
- AuditTrail: Record-keeping per Article 12
- ComplianceReport: Documentation generation

Example:
    from apce.compliance import Watermarker
    
    wm = Watermarker(model_id="gpt-4", organization="Acme")
    marked = wm.watermark_text("AI response...")
    
    valid, meta = wm.verify_text(marked)
"""

from .watermark import (
    Watermarker,
    TextWatermarker,
    HashWatermarker,
    WatermarkMetadata,
)

__all__ = [
    "Watermarker",
    "TextWatermarker", 
    "HashWatermarker",
    "WatermarkMetadata",
]
