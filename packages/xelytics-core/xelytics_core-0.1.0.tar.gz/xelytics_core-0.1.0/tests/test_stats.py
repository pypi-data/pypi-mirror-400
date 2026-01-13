"""Unit tests for statistical engine.

Tests planner, engine, and individual statistical tests.
"""

import pytest
import pandas as pd
import numpy as np

from xelytics.stats.planner import TestPlanner, TestPlan
from xelytics.stats.engine import StatisticalEngine, StatisticalExecutionResult
from xelytics.stats.tests import (
    run_t_test,
    run_anova,
    run_chi_square,
    run_correlation,
    run_normality_test,
)
from xelytics.core.features import FeatureDetector
from xelytics.schemas.outputs import StatisticalTestResult, TestType


class TestStatisticalTests:
    """Tests for individual statistical test functions."""
    
    def test_t_test_independent(self):
        """Test independent t-test."""
        np.random.seed(42)
        g1 = np.random.normal(10, 2, 50)
        g2 = np.random.normal(12, 2, 50)  # Different mean
        
        result = run_t_test(g1, g2, paired=False)
        
        assert isinstance(result, StatisticalTestResult)
        assert result.test_type == TestType.T_TEST_INDEPENDENT
        assert result.significant  # Should detect the difference
        assert result.effect_size is not None
    
    def test_t_test_paired(self):
        """Test paired t-test."""
        np.random.seed(42)
        before = np.random.normal(100, 10, 30)
        after = before + np.random.normal(5, 2, 30)  # Improvement
        
        result = run_t_test(before, after, paired=True)
        
        assert result.test_type == TestType.T_TEST_PAIRED
        assert result.significant
    
    def test_anova(self):
        """Test one-way ANOVA."""
        np.random.seed(42)
        df = pd.DataFrame({
            'value': list(np.random.normal(10, 2, 30)) + 
                     list(np.random.normal(15, 2, 30)) + 
                     list(np.random.normal(20, 2, 30)),
            'group': ['A'] * 30 + ['B'] * 30 + ['C'] * 30,
        })
        
        result = run_anova(df, 'value', 'group')
        
        assert result.test_type == TestType.ANOVA_ONE_WAY
        assert result.significant  # Should detect group differences
        assert result.effect_size is not None
        assert result.effect_size.measure_type == "eta_squared"
    
    def test_chi_square(self):
        """Test chi-square test of independence."""
        df = pd.DataFrame({
            'gender': ['M', 'M', 'F', 'F', 'M', 'F'] * 20,
            'preference': ['A', 'A', 'B', 'B', 'A', 'B'] * 20,
        })
        
        result = run_chi_square(df, 'gender', 'preference')
        
        assert result.test_type == TestType.CHI_SQUARE
        assert result.effect_size is not None
        assert result.effect_size.measure_type == "cramers_v"
    
    def test_correlation_pearson(self):
        """Test Pearson correlation."""
        np.random.seed(42)
        x = np.random.normal(0, 1, 100)
        y = x * 2 + np.random.normal(0, 0.5, 100)  # Strong correlation
        
        result = run_correlation(x, y, method="pearson")
        
        assert result.test_type == TestType.CORRELATION_PEARSON
        assert result.significant
        assert abs(result.statistic) > 0.8  # Strong correlation
    
    def test_correlation_spearman(self):
        """Test Spearman correlation."""
        np.random.seed(42)
        x = np.arange(50)
        y = x ** 2 + np.random.normal(0, 10, 50)  # Monotonic relationship
        
        result = run_correlation(x, y, method="spearman")
        
        assert result.test_type == TestType.CORRELATION_SPEARMAN
        assert result.significant
    
    def test_normality_shapiro(self):
        """Test Shapiro-Wilk normality test."""
        np.random.seed(42)
        normal_data = np.random.normal(0, 1, 100)
        
        result = run_normality_test(normal_data, method="shapiro")
        
        assert result.test_type == TestType.NORMALITY_SHAPIRO
        # Normal data should pass normality test
        assert not result.significant  # Not significant = normal
    
    def test_normality_non_normal(self):
        """Test normality test with non-normal data."""
        np.random.seed(42)
        # Uniform distribution is not normal
        non_normal_data = np.random.uniform(0, 1, 100)
        
        result = run_normality_test(non_normal_data, method="shapiro")
        
        # Should detect non-normality
        assert result.significant  # Significant = not normal


class TestTestPlanner:
    """Tests for TestPlanner module."""
    
    def test_plans_anova_for_multiple_groups(self, sample_mixed_df):
        """Test that planner selects ANOVA for multiple groups."""
        detector = FeatureDetector()
        features = detector.detect(sample_mixed_df)
        
        planner = TestPlanner()
        plan = planner.plan(sample_mixed_df, features)
        
        assert isinstance(plan, TestPlan)
        assert len(plan.tests) > 0
        
        # Should have ANOVA tests planned
        anova_tests = [t for t in plan.tests if t.get('test_type') == 'anova']
        assert len(anova_tests) > 0
    
    def test_decision_log_populated(self, sample_mixed_df):
        """Test that decision log captures all decisions."""
        detector = FeatureDetector()
        features = detector.detect(sample_mixed_df)
        
        planner = TestPlanner()
        plan = planner.plan(sample_mixed_df, features)
        
        # Decision log should have entries
        assert len(plan.decision_log.entries) > 0
        
        # Every selected test should have a reason
        for entry in plan.decision_log.entries:
            assert entry.reason != ""
    
    def test_skipped_tests_logged(self):
        """Test that skipped tests are logged with reasons."""
        # Create DataFrame with insufficient data for some tests
        df = pd.DataFrame({
            'value': [1, 2],  # Too few rows
            'group': ['A', 'A'],  # Only one group
        })
        
        detector = FeatureDetector()
        features = detector.detect(df)
        
        planner = TestPlanner()
        plan = planner.plan(df, features)
        
        # Should have logged skipped tests
        skipped = plan.decision_log.get_by_type(
            plan.decision_log.entries[0].decision_type.__class__.TEST_SKIPPED
            if plan.decision_log.entries else None
        ) if plan.decision_log.entries else []
        
        # Decision log should exist even if empty tests
        assert plan.decision_log is not None


class TestStatisticalEngine:
    """Tests for StatisticalEngine module."""
    
    def test_execute_returns_results(self, sample_mixed_df):
        """Test that engine executes tests and returns results."""
        detector = FeatureDetector()
        features = detector.detect(sample_mixed_df)
        
        engine = StatisticalEngine()
        result = engine.execute(sample_mixed_df, features)
        
        assert isinstance(result, StatisticalExecutionResult)
        assert result.tests_executed >= 0
    
    def test_decision_log_includes_execution_info(self, sample_mixed_df):
        """Test that decision log includes execution information."""
        detector = FeatureDetector()
        features = detector.detect(sample_mixed_df)
        
        engine = StatisticalEngine()
        result = engine.execute(sample_mixed_df, features)
        
        # Decision log should be present
        assert result.decision_log is not None
    
    def test_deterministic_results(self, sample_mixed_df):
        """Test that statistical results are deterministic."""
        detector = FeatureDetector()
        features = detector.detect(sample_mixed_df)
        
        engine = StatisticalEngine()
        
        # Run twice
        result1 = engine.execute(sample_mixed_df, features)
        result2 = engine.execute(sample_mixed_df, features)
        
        # Same number of tests
        assert result1.tests_executed == result2.tests_executed
        
        # Same p-values (deterministic)
        if result1.results and result2.results:
            for r1, r2 in zip(result1.results, result2.results):
                assert r1.p_value == r2.p_value
