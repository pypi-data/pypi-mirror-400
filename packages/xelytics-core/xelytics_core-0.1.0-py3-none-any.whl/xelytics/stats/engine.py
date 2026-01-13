"""Statistical engine module.

Orchestrates test planning and execution.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from xelytics.schemas.outputs import StatisticalTestResult
from xelytics.schemas.metadata import DecisionLog
from xelytics.core.features import FeatureDetectionResult
from xelytics.stats.planner import TestPlanner, TestPlan
from xelytics.stats.tests import (
    run_t_test,
    run_anova,
    run_chi_square,
    run_correlation,
    run_normality_test,
)


@dataclass
class StatisticalExecutionResult:
    """Result of statistical execution."""
    results: List[StatisticalTestResult]
    decision_log: DecisionLog
    tests_executed: int
    tests_failed: int


class StatisticalEngine:
    """Statistical analysis engine.
    
    Orchestrates test planning and execution.
    All decisions are logged.
    """
    
    def __init__(self, alpha: float = 0.05):
        """Initialize statistical engine.
        
        Args:
            alpha: Significance level
        """
        self.alpha = alpha
        self.planner = TestPlanner(alpha=alpha)
    
    def execute(
        self,
        df: pd.DataFrame,
        features: FeatureDetectionResult,
    ) -> StatisticalExecutionResult:
        """Execute statistical analysis.
        
        Args:
            df: Input DataFrame
            features: Feature detection result
            
        Returns:
            StatisticalExecutionResult with all results
        """
        # Plan tests
        plan = self.planner.plan(df, features)
        
        # Execute tests
        results = []
        tests_failed = 0
        
        for test_spec in plan.tests:
            try:
                result = self._execute_test(df, test_spec)
                if result:
                    results.append(result)
            except Exception as e:
                tests_failed += 1
                # Log failure but continue
                plan.decision_log.add_test_skipped(
                    test_name=test_spec.get("test_type", "unknown"),
                    columns=self._get_columns_from_spec(test_spec),
                    reason=f"Execution failed: {str(e)}",
                )
        
        return StatisticalExecutionResult(
            results=results,
            decision_log=plan.decision_log,
            tests_executed=len(results),
            tests_failed=tests_failed,
        )
    
    def _execute_test(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> Optional[StatisticalTestResult]:
        """Execute a single test from specification.
        
        Args:
            df: Data
            spec: Test specification
            
        Returns:
            StatisticalTestResult or None if failed
        """
        test_type = spec.get("test_type")
        
        if test_type == "t_test":
            return self._execute_t_test(df, spec)
        elif test_type == "anova":
            return self._execute_anova(df, spec)
        elif test_type == "chi_square":
            return self._execute_chi_square(df, spec)
        elif test_type == "correlation":
            return self._execute_correlation(df, spec)
        elif test_type == "normality":
            return self._execute_normality(df, spec)
        else:
            return None
    
    def _execute_t_test(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> StatisticalTestResult:
        """Execute t-test."""
        dep_var = spec["dependent_var"]
        ind_var = spec["independent_var"]
        
        # Get groups
        groups = list(df.groupby(ind_var)[dep_var])
        if len(groups) != 2:
            raise ValueError(f"T-test requires exactly 2 groups, got {len(groups)}")
        
        g1 = groups[0][1].dropna().values
        g2 = groups[1][1].dropna().values
        
        result = run_t_test(g1, g2, paired=False, alpha=self.alpha)
        result.columns = [dep_var, ind_var]
        result.decision_reason = f"Selected for comparing '{dep_var}' across 2 groups of '{ind_var}'"
        
        return result
    
    def _execute_anova(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> StatisticalTestResult:
        """Execute ANOVA."""
        dep_var = spec["dependent_var"]
        ind_var = spec["independent_var"]
        
        result = run_anova(df, dep_var, ind_var, alpha=self.alpha)
        result.decision_reason = f"Selected for comparing '{dep_var}' across multiple groups of '{ind_var}'"
        
        return result
    
    def _execute_chi_square(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> StatisticalTestResult:
        """Execute chi-square test."""
        col1 = spec["col1"]
        col2 = spec["col2"]
        
        result = run_chi_square(df, col1, col2, alpha=self.alpha)
        result.decision_reason = f"Selected for testing association between '{col1}' and '{col2}'"
        
        return result
    
    def _execute_correlation(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> StatisticalTestResult:
        """Execute correlation test."""
        col1 = spec["col1"]
        col2 = spec["col2"]
        method = spec.get("method", "pearson")
        
        x = df[col1].values
        y = df[col2].values
        
        result = run_correlation(x, y, method=method, alpha=self.alpha)
        result.columns = [col1, col2]
        result.decision_reason = f"Selected for testing relationship between '{col1}' and '{col2}'"
        
        return result
    
    def _execute_normality(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> StatisticalTestResult:
        """Execute normality test."""
        column = spec["column"]
        method = spec.get("method", "shapiro")
        
        data = df[column].values
        
        result = run_normality_test(data, method=method, alpha=self.alpha)
        result.columns = [column]
        result.decision_reason = f"Selected for testing distribution normality of '{column}'"
        
        return result
    
    def _get_columns_from_spec(self, spec: Dict[str, Any]) -> List[str]:
        """Extract column names from test specification."""
        columns = []
        for key in ["column", "col1", "col2", "dependent_var", "independent_var"]:
            if key in spec:
                columns.append(spec[key])
        return columns
