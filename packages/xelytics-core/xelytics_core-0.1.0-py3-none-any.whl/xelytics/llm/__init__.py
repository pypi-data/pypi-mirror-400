"""LLM modules for xelytics.

LLM integration is LATE BY DESIGN.
LLM is for narration only - does not affect analytics results.
"""

from xelytics.llm.provider import LLMProvider, LLMResult
from xelytics.llm.narrator import InsightNarrator

__all__ = [
    "LLMProvider",
    "LLMResult",
    "InsightNarrator",
]
