"""Test planner module.

Determines which tests to run based on data characteristics.
Emits machine-readable decision log - NO AUTO MAGIC.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd
import numpy as np

from xelytics.schemas.outputs import TestType
from xelytics.schemas.metadata import DecisionLog
from xelytics.core.features import FeatureDetectionResult


@dataclass
class TestPlan:
    """Plan of tests to execute."""
    tests: List[Dict[str, Any]]
    decision_log: DecisionLog


class TestPlanner:
    """Statistical test planner.
    
    Determines which tests to run based on data characteristics.
    
    NO AUTO MAGIC:
    - Planning must emit machine-readable decision log
    - No implicit defaults based on sample size alone
    - If a test is chosen, the reason must be in metadata, always
    """
    
    # Configuration
    MIN_SAMPLE_SIZE = 3
    MIN_GROUPS_FOR_ANOVA = 2
    MAX_CATEGORIES_FOR_CHI_SQUARE = 20
    
    def __init__(self, alpha: float = 0.05):
        """Initialize test planner.
        
        Args:
            alpha: Significance level
        """
        self.alpha = alpha
        self.decision_log = DecisionLog()
    
    def plan(
        self,
        df: pd.DataFrame,
        features: FeatureDetectionResult,
    ) -> TestPlan:
        """Create test execution plan.
        
        Args:
            df: Input DataFrame
            features: Feature detection result
            
        Returns:
            TestPlan with tests to execute and decision log
        """
        self.decision_log = DecisionLog()
        tests = []
        
        numeric_cols = features.numeric_columns
        categorical_cols = features.categorical_columns
        groupable_cols = features.groupable_columns
        
        # Plan numeric comparisons (ANOVA/t-tests)
        tests.extend(self._plan_numeric_comparisons(df, numeric_cols, groupable_cols))
        
        # Plan categorical associations (chi-square)
        tests.extend(self._plan_categorical_associations(df, categorical_cols))
        
        # Plan correlations
        tests.extend(self._plan_correlations(df, numeric_cols))
        
        # Plan normality tests for key numeric columns
        tests.extend(self._plan_normality_tests(df, numeric_cols))
        
        return TestPlan(
            tests=tests,
            decision_log=self.decision_log,
        )
    
    def _plan_numeric_comparisons(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str],
        groupable_cols: List[str],
    ) -> List[Dict[str, Any]]:
        """Plan tests comparing numeric across groups.
        
        Args:
            df: Data
            numeric_cols: Numeric columns
            groupable_cols: Columns suitable for grouping
            
        Returns:
            List of test specifications
        """
        tests = []
        
        for num_col in numeric_cols[:5]:  # Limit to top 5 numeric columns
            for group_col in groupable_cols[:3]:  # Limit to top 3 groupable
                if num_col == group_col:
                    continue
                
                # Check data requirements
                n_groups = df[group_col].nunique()
                valid_data = df[[num_col, group_col]].dropna()
                
                if len(valid_data) < self.MIN_SAMPLE_SIZE:
                    self.decision_log.add_test_skipped(
                        test_name="ANOVA/t-test",
                        columns=[num_col, group_col],
                        reason=f"Insufficient data: {len(valid_data)} valid rows",
                        context={"min_required": self.MIN_SAMPLE_SIZE},
                    )
                    continue
                
                if n_groups < 2:
                    self.decision_log.add_test_skipped(
                        test_name="ANOVA/t-test",
                        columns=[num_col, group_col],
                        reason=f"Insufficient groups: {n_groups} groups",
                        context={"min_required": 2},
                    )
                    continue
                
                # Determine test type based on number of groups
                if n_groups == 2:
                    test_type = "t_test"
                    test_name = "Independent t-test"
                    reason = f"2 groups detected in '{group_col}', selecting t-test for '{num_col}'"
                else:
                    test_type = "anova"
                    test_name = "One-way ANOVA"
                    reason = f"{n_groups} groups detected in '{group_col}', selecting ANOVA for '{num_col}'"
                
                tests.append({
                    "test_type": test_type,
                    "dependent_var": num_col,
                    "independent_var": group_col,
                })
                
                self.decision_log.add_test_selected(
                    test_name=test_name,
                    columns=[num_col, group_col],
                    reason=reason,
                    context={"n_groups": n_groups, "n_valid": len(valid_data)},
                )
        
        return tests
    
    def _plan_categorical_associations(
        self,
        df: pd.DataFrame,
        categorical_cols: List[str],
    ) -> List[Dict[str, Any]]:
        """Plan chi-square tests for categorical associations.
        
        Args:
            df: Data
            categorical_cols: Categorical columns
            
        Returns:
            List of test specifications
        """
        tests = []
        tested_pairs: Set[Tuple[str, str]] = set()
        
        for i, col1 in enumerate(categorical_cols[:5]):
            for col2 in categorical_cols[i+1:5]:
                pair = tuple(sorted([col1, col2]))
                if pair in tested_pairs:
                    continue
                tested_pairs.add(pair)
                
                # Check cardinality
                n1 = df[col1].nunique()
                n2 = df[col2].nunique()
                
                if n1 > self.MAX_CATEGORIES_FOR_CHI_SQUARE or n2 > self.MAX_CATEGORIES_FOR_CHI_SQUARE:
                    self.decision_log.add_test_skipped(
                        test_name="Chi-square",
                        columns=[col1, col2],
                        reason=f"Too many categories ({n1} x {n2})",
                        context={"max_allowed": self.MAX_CATEGORIES_FOR_CHI_SQUARE},
                    )
                    continue
                
                # Check data requirements
                valid_data = df[[col1, col2]].dropna()
                if len(valid_data) < self.MIN_SAMPLE_SIZE:
                    self.decision_log.add_test_skipped(
                        test_name="Chi-square",
                        columns=[col1, col2],
                        reason=f"Insufficient data: {len(valid_data)} valid rows",
                    )
                    continue
                
                tests.append({
                    "test_type": "chi_square",
                    "col1": col1,
                    "col2": col2,
                })
                
                self.decision_log.add_test_selected(
                    test_name="Chi-square",
                    columns=[col1, col2],
                    reason=f"Testing association between categorical variables ({n1} x {n2} categories)",
                    context={"n1": n1, "n2": n2, "n_valid": len(valid_data)},
                )
        
        return tests
    
    def _plan_correlations(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str],
    ) -> List[Dict[str, Any]]:
        """Plan correlation tests for numeric pairs.
        
        Args:
            df: Data
            numeric_cols: Numeric columns
            
        Returns:
            List of test specifications
        """
        tests = []
        tested_pairs: Set[Tuple[str, str]] = set()
        
        for i, col1 in enumerate(numeric_cols[:5]):
            for col2 in numeric_cols[i+1:5]:
                pair = tuple(sorted([col1, col2]))
                if pair in tested_pairs:
                    continue
                tested_pairs.add(pair)
                
                # Check data requirements
                valid_data = df[[col1, col2]].dropna()
                if len(valid_data) < 3:
                    self.decision_log.add_test_skipped(
                        test_name="Correlation",
                        columns=[col1, col2],
                        reason=f"Insufficient data: {len(valid_data)} valid pairs",
                    )
                    continue
                
                tests.append({
                    "test_type": "correlation",
                    "col1": col1,
                    "col2": col2,
                    "method": "pearson",
                })
                
                self.decision_log.add_test_selected(
                    test_name="Pearson correlation",
                    columns=[col1, col2],
                    reason=f"Testing linear relationship between numeric variables",
                    context={"n_valid_pairs": len(valid_data)},
                )
        
        return tests
    
    def _plan_normality_tests(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str],
    ) -> List[Dict[str, Any]]:
        """Plan normality tests for numeric columns.
        
        Args:
            df: Data
            numeric_cols: Numeric columns
            
        Returns:
            List of test specifications
        """
        tests = []
        
        for col in numeric_cols[:5]:  # Limit to top 5
            valid_data = df[col].dropna()
            
            if len(valid_data) < 3:
                self.decision_log.add_test_skipped(
                    test_name="Normality test",
                    columns=[col],
                    reason=f"Insufficient data: {len(valid_data)} values",
                )
                continue
            
            tests.append({
                "test_type": "normality",
                "column": col,
                "method": "shapiro",
            })
            
            self.decision_log.add_test_selected(
                test_name="Shapiro-Wilk normality test",
                columns=[col],
                reason="Testing distribution normality for parametric test assumptions",
                context={"n_values": len(valid_data)},
            )
        
        return tests
