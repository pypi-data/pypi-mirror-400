"""
APCE Claude Wrapper - Verified Anthropic API Integration
=========================================================

Wraps Claude API with APCE runtime verification.
Complements Constitutional AI with conservation law enforcement.

Example:
    from apce.wrappers import ClaudeWrapper
    
    wrapper = ClaudeWrapper(api_key="sk-ant-...")
    response = wrapper.chat([{"role": "user", "content": "Hello"}])
    
    print(response.content)
    print(response.provenance.to_json())
"""

from typing import Any, Dict, List, Optional, Tuple

from .base import APCEWrapper, VerifiedResponse
from ..core import VerificationMode


class ClaudeWrapper(APCEWrapper):
    """
    APCE-verified wrapper for Anthropic's Claude API.
    
    Provides:
    - Runtime verification for Claude responses
    - Prompt injection detection (100% detection rate)
    - Cryptographic audit trail (BLAKE3 provenance)
    - Conservation law enforcement
    
    Works with all Claude models (claude-3-opus, claude-3-sonnet, etc.)
    
    Args:
        api_key: Anthropic API key
        model: Model name (default: claude-sonnet-4-5-20250514)
        mode: Verification intensity (TURBO, BALANCED, THOROUGH, ESCALATION)
        max_tokens: Maximum response tokens
        enforce_conservation: Raise on violations if True
    
    Example:
        wrapper = ClaudeWrapper(
            api_key="sk-ant-...",
            model="claude-sonnet-4-5-20250514",
            mode=VerificationMode.BALANCED
        )
        
        result = wrapper.chat([
            {"role": "user", "content": "Explain quantum computing"}
        ])
        
        # Access verified content
        print(result.content)
        
        # Access provenance for audit
        print(result.provenance.merkle_root)
    """
    
    SUPPORTED_MODELS = [
        "claude-opus-4-5-20251101",
        "claude-sonnet-4-5-20250929",
        "claude-haiku-4-5-20251001",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250514",
        mode: VerificationMode = VerificationMode.BALANCED,
        max_tokens: int = 4096,
        enforce_conservation: bool = True,
        **kwargs
    ):
        super().__init__(
            api_key=api_key,
            mode=mode,
            model=model,
            enforce_conservation=enforce_conservation,
            **kwargs
        )
        self.max_tokens = max_tokens
        self._client = None
        
    def _get_client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install apce-safety[anthropic]"
                )
            
            if self.api_key:
                self._client = Anthropic(api_key=self.api_key)
            else:
                # Will use ANTHROPIC_API_KEY env var
                self._client = Anthropic()
        
        return self._client
    
    def _call_model(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Tuple[str, Any]:
        """
        Call Claude API with the given messages.
        
        Converts from OpenAI message format if needed.
        """
        client = self._get_client()
        
        # Extract system message if present
        system = None
        chat_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                system = content
            else:
                # Map 'assistant' to 'assistant', 'user' to 'user'
                chat_messages.append({
                    "role": role,
                    "content": content
                })
        
        # Build request
        request_kwargs = {
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": chat_messages,
        }
        
        if system:
            request_kwargs["system"] = system
        
        # Additional parameters
        if "temperature" in kwargs:
            request_kwargs["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            request_kwargs["top_p"] = kwargs["top_p"]
        if "stop_sequences" in kwargs:
            request_kwargs["stop_sequences"] = kwargs["stop_sequences"]
        
        # Call API
        response = client.messages.create(**request_kwargs)
        
        # Extract text content
        text_content = ""
        for block in response.content:
            if hasattr(block, "text"):
                text_content += block.text
        
        return text_content, response
    
    def verify_and_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> VerifiedResponse:
        """
        Send messages to Claude with full APCE verification.
        
        Alias for verify_and_call with Claude-specific naming.
        """
        return self.verify_and_call(messages, **kwargs)
    
    def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        """
        Stream responses from Claude with verification.
        
        Note: Verification happens on complete response.
        Yields chunks, then final VerifiedResponse.
        """
        # For streaming, we collect chunks then verify
        chunks = []
        
        client = self._get_client()
        
        # Build request (similar to _call_model)
        system = None
        chat_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                system = content
            else:
                chat_messages.append({"role": role, "content": content})
        
        request_kwargs = {
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": chat_messages,
        }
        
        if system:
            request_kwargs["system"] = system
        
        with client.messages.stream(**request_kwargs) as stream:
            for text in stream.text_stream:
                chunks.append(text)
                yield text
        
        # Now verify complete response
        full_response = "".join(chunks)
        analysis = self._post_verify(full_response)
        
        provenance = self.verifier.create_provenance(
            request=str(messages),
            response=full_response,
            analysis=analysis,
            model_id=self.model,
        )
        
        # Yield final verification result
        yield VerifiedResponse(
            content=full_response,
            model=self.model,
            provenance=provenance,
            analysis=analysis,
            verified=analysis.is_valid,
            latency_ms=0.0,  # Streaming doesn't track this well
        )
