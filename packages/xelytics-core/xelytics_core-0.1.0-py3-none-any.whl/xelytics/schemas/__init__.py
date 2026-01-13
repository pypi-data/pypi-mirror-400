"""Schema definitions for xelytics-core.

All input/output contracts are defined here.
"""

from xelytics.schemas.config import AnalysisConfig
from xelytics.schemas.outputs import (
    AnalysisResult,
    DatasetSummary,
    StatisticalTestResult,
    VisualizationSpec,
    Insight,
    RunMetadata,
)
from xelytics.schemas.inputs import DatasetInput

__all__ = [
    "AnalysisConfig",
    "AnalysisResult",
    "DatasetSummary",
    "StatisticalTestResult",
    "VisualizationSpec",
    "Insight",
    "RunMetadata",
    "DatasetInput",
]
