"""LLM Provider interface.

Defines the contract for all LLM providers.
Analytics code depends ONLY on this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum


class ProviderType(str, Enum):
    """Supported LLM provider types."""
    OPENAI = "openai"
    GROK = "grok"  # Deferred until Phase 8 passes


@dataclass
class LLMResult:
    """Unified result from any LLM provider.
    
    This is the contract that all providers must honor.
    Analytics code depends ONLY on this class.
    """
    content: str
    parsed_json: Optional[Dict[str, Any]] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    retries: int = 0
    provider: str = ""
    latency_ms: int = 0
    
    def is_json_valid(self) -> bool:
        """Check if JSON was successfully parsed."""
        return self.parsed_json is not None


class LLMProvider(ABC):
    """Abstract base class for LLM providers.
    
    All providers must implement this interface.
    Analytics code calls only these methods.
    
    Provider implementations should:
    - Handle retries internally
    - Return LLMResult always
    - Never throw for retryable errors
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass
    
    @property
    def supports_json_schema(self) -> bool:
        """Whether provider supports JSON schema enforcement."""
        return False
    
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
        timeout_seconds: int = 30,
    ) -> LLMResult:
        """Generate text completion.
        
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
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if provider is available.
        
        Returns:
            True if provider is healthy
        """
        pass


class NoOpProvider(LLMProvider):
    """No-operation provider for when LLM is disabled.
    
    Returns empty results without making any API calls.
    """
    
    @property
    def name(self) -> str:
        return "noop"
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
        timeout_seconds: int = 30,
    ) -> LLMResult:
        """Return empty result."""
        return LLMResult(
            content="",
            provider=self.name,
        )
    
    def health_check(self) -> bool:
        """Always healthy."""
        return True
