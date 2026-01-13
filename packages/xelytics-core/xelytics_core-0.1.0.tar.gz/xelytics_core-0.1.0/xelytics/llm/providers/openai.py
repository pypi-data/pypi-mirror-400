"""OpenAI LLM Provider implementation.

Implements the LLM provider interface for OpenAI API.
This is the FIRST provider - Grok is deferred until Phase 8 passes.
"""

import os
import time
import json
from typing import Any, Dict, Optional

from xelytics.llm.provider import LLMProvider, LLMResult


class OpenAIProvider(LLMProvider):
    """OpenAI API provider.
    
    Implements LLMProvider for OpenAI's GPT models.
    API key from environment variable only.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
    ):
        """Initialize OpenAI provider.
        
        Args:
            model: Model to use (default: gpt-4o-mini)
            api_key: API key. If not provided, reads from OPENAI_API_KEY env var
        """
        self._model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._client = None
    
    @property
    def name(self) -> str:
        return "openai"
    
    @property
    def supports_json_schema(self) -> bool:
        return True
    
    def _get_client(self):
        """Lazily initialize OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Install with: pip install xelytics-core[llm]"
                )
        return self._client
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
        timeout_seconds: int = 30,
    ) -> LLMResult:
        """Generate text using OpenAI API.
        
        Args:
            system_prompt: System instructions
            user_prompt: User message
            response_schema: Optional JSON schema for response
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            timeout_seconds: Request timeout
            
        Returns:
            LLMResult with generated content
        """
        start_time = time.time()
        retries = 0
        max_retries = 3
        
        while retries < max_retries:
            try:
                client = self._get_client()
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
                
                kwargs = {
                    "model": self._model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "timeout": timeout_seconds,
                }
                
                # Add JSON mode if schema provided
                if response_schema:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = client.chat.completions.create(**kwargs)
                
                content = response.choices[0].message.content or ""
                
                # Parse JSON if schema was requested
                parsed_json = None
                if response_schema:
                    try:
                        parsed_json = json.loads(content)
                    except json.JSONDecodeError:
                        pass
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                return LLMResult(
                    content=content,
                    parsed_json=parsed_json,
                    input_tokens=response.usage.prompt_tokens if response.usage else 0,
                    output_tokens=response.usage.completion_tokens if response.usage else 0,
                    total_tokens=response.usage.total_tokens if response.usage else 0,
                    retries=retries,
                    provider=self.name,
                    latency_ms=latency_ms,
                )
                
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    latency_ms = int((time.time() - start_time) * 1000)
                    return LLMResult(
                        content=f"Error: {str(e)}",
                        retries=retries,
                        provider=self.name,
                        latency_ms=latency_ms,
                    )
                time.sleep(1)  # Wait before retry
        
        # Should not reach here
        return LLMResult(content="", provider=self.name)
    
    def health_check(self) -> bool:
        """Check if OpenAI API is available.
        
        Returns:
            True if API is reachable and key is valid
        """
        if not self._api_key:
            return False
        
        try:
            client = self._get_client()
            # Simple ping - list models
            client.models.list()
            return True
        except Exception:
            return False
