"""Core analytics modules for xelytics.

Contains ingestion, profiling, and feature detection.
"""

from xelytics.core.profiler import DataProfiler
from xelytics.core.features import FeatureDetector
from xelytics.core.ingestion import DataIngestion

__all__ = [
    "DataProfiler",
    "FeatureDetector",
    "DataIngestion",
]
