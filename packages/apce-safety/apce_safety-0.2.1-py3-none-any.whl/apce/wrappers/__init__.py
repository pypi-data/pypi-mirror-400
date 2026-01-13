"""
APCE Wrappers - Model-Specific Integrations
============================================

Pre-built wrappers for major LLM APIs and frameworks:
- ClaudeWrapper: Anthropic Claude API
- GPTWrapper: OpenAI Chat Completions API  
- LlamaWrapper: Local Hugging Face Transformers

All wrappers provide:
- Pre-call verification (injection detection)
- Post-call verification (conservation analysis)
- Cryptographic provenance (audit trails)

Example:
    from apce.wrappers import ClaudeWrapper
    
    claude = ClaudeWrapper(api_key="sk-ant-...")
    result = claude.chat([{"role": "user", "content": "Hello"}])
"""

from .base import APCEWrapper, VerifiedResponse

# Lazy imports to avoid requiring all dependencies
def __getattr__(name):
    if name == "ClaudeWrapper":
        from .anthropic import ClaudeWrapper
        return ClaudeWrapper
    elif name in ("GPTWrapper", "OpenAIWrapper"):
        from .openai import GPTWrapper
        return GPTWrapper
    elif name in ("LlamaWrapper", "TransformersWrapper", "HuggingFaceWrapper"):
        from .llama import LlamaWrapper
        return LlamaWrapper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "APCEWrapper",
    "VerifiedResponse",
    "ClaudeWrapper",
    "GPTWrapper",
    "OpenAIWrapper",
    "LlamaWrapper",
    "TransformersWrapper",
    "HuggingFaceWrapper",
]
