"""Statistical analysis modules for xelytics.

Contains test planning, execution, and metadata capture.
"""

from xelytics.stats.engine import StatisticalEngine
from xelytics.stats.planner import TestPlanner
from xelytics.stats.tests import (
    run_t_test,
    run_anova,
    run_chi_square,
    run_correlation,
    run_normality_test,
)

__all__ = [
    "StatisticalEngine",
    "TestPlanner",
    "run_t_test",
    "run_anova",
    "run_chi_square",
    "run_correlation",
    "run_normality_test",
]
