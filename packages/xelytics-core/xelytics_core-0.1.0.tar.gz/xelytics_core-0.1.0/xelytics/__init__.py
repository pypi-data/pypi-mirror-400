"""Xelytics-Core: Pure Analytics Engine.

This is the public API. Everything else is an implementation detail.
"""

from xelytics.__version__ import __version__
from xelytics.schemas.config import AnalysisConfig
from xelytics.schemas.outputs import AnalysisResult
from xelytics.engine import analyze

__all__ = [
    "__version__",
    "analyze",
    "AnalysisConfig",
    "AnalysisResult",
]
