"""Golden output and determinism tests.

Tests to ensure:
1. Same input → same output (determinism)
2. Output matches expected golden values (regression)
"""

import pytest
import pandas as pd
import numpy as np
import json
import hashlib

from xelytics import analyze, AnalysisConfig


class TestDeterminism:
    """Tests that same input produces same output."""
    
    def test_analyze_deterministic(self, golden_dataset):
        """Test that analyze() produces identical output across runs."""
        config = AnalysisConfig(
            mode="automated",
            enable_llm_insights=False,  # Disable LLM for determinism
        )
        
        hashes = []
        for _ in range(3):
            result = analyze(golden_dataset, mode="automated", config=config)
            # Hash the core output
            output = {
                "row_count": result.summary.row_count,
                "column_count": result.summary.column_count,
                "tests_executed": result.metadata.tests_executed,
                "numeric_columns": sorted(result.summary.numeric_columns),
                "categorical_columns": sorted(result.summary.categorical_columns),
            }
            hash_val = hashlib.md5(json.dumps(output, sort_keys=True).encode()).hexdigest()
            hashes.append(hash_val)
        
        assert len(set(hashes)) == 1, f"Non-deterministic output: {hashes}"
    
    def test_statistical_results_deterministic(self, golden_dataset):
        """Test that statistical test results are deterministic."""
        config = AnalysisConfig(mode="automated", enable_llm_insights=False)
        
        p_values_runs = []
        for _ in range(3):
            result = analyze(golden_dataset, mode="automated", config=config)
            p_values = [r.p_value for r in result.statistics]
            p_values_runs.append(tuple(p_values))
        
        assert len(set(p_values_runs)) == 1, "P-values differ across runs"
    
    def test_insight_generation_deterministic(self, golden_dataset):
        """Test that insight generation is deterministic."""
        config = AnalysisConfig(mode="automated", enable_llm_insights=False)
        
        insight_titles_runs = []
        for _ in range(3):
            result = analyze(golden_dataset, mode="automated", config=config)
            titles = sorted([i.title for i in result.insights])
            insight_titles_runs.append(tuple(titles))
        
        assert len(set(insight_titles_runs)) == 1, "Insights differ across runs"


class TestGoldenOutput:
    """Golden output regression tests.
    
    These tests verify that key outputs match expected values.
    If the expected values change, investigate why before updating.
    """
    
    def test_golden_dataset_row_count(self, golden_dataset):
        """Test expected row count."""
        result = analyze(golden_dataset, mode="automated")
        assert result.summary.row_count == 10
    
    def test_golden_dataset_column_count(self, golden_dataset):
        """Test expected column count."""
        result = analyze(golden_dataset, mode="automated")
        assert result.summary.column_count == 4
    
    def test_golden_dataset_numeric_columns(self, golden_dataset):
        """Test expected numeric column detection."""
        result = analyze(golden_dataset, mode="automated")
        
        expected_numeric = ['age', 'income']
        assert sorted(result.summary.numeric_columns) == sorted(expected_numeric)
    
    def test_golden_dataset_categorical_columns(self, golden_dataset):
        """Test expected categorical column detection."""
        result = analyze(golden_dataset, mode="automated")
        
        expected_categorical = ['education', 'region']
        assert sorted(result.summary.categorical_columns) == sorted(expected_categorical)
    
    def test_golden_dataset_no_missing(self, golden_dataset):
        """Test that golden dataset has no missing values."""
        result = analyze(golden_dataset, mode="automated")
        assert result.summary.total_missing_cells == 0
    
    def test_json_serialization_roundtrip(self, golden_dataset):
        """Test that JSON serialization is lossless."""
        from xelytics.schemas.outputs import AnalysisResult
        
        result = analyze(golden_dataset, mode="automated")
        
        # Serialize to JSON
        json_str = result.to_json()
        
        # Deserialize
        restored = AnalysisResult.from_json(json_str)
        
        # Compare key fields
        assert restored.summary.row_count == result.summary.row_count
        assert restored.summary.column_count == result.summary.column_count
        assert len(restored.statistics) == len(result.statistics)
        assert len(restored.insights) == len(result.insights)


class TestBackwardCompatibility:
    """Backward compatibility tests.
    
    Ensures schema changes don't break existing integrations.
    """
    
    def test_analysis_result_has_required_fields(self, sample_mixed_df):
        """Test that AnalysisResult has all required fields."""
        result = analyze(sample_mixed_df, mode="automated")
        
        # Required top-level fields (per API_CONTRACT.md)
        assert hasattr(result, 'summary')
        assert hasattr(result, 'statistics')
        assert hasattr(result, 'visualizations')
        assert hasattr(result, 'insights')
        assert hasattr(result, 'metadata')
    
    def test_dataset_summary_fields(self, sample_mixed_df):
        """Test that DatasetSummary has expected fields."""
        result = analyze(sample_mixed_df, mode="automated")
        summary = result.summary
        
        assert hasattr(summary, 'row_count')
        assert hasattr(summary, 'column_count')
        assert hasattr(summary, 'numeric_columns')
        assert hasattr(summary, 'categorical_columns')
        assert hasattr(summary, 'column_profiles')
    
    def test_statistical_result_fields(self, sample_mixed_df):
        """Test that StatisticalTestResult has expected fields."""
        result = analyze(sample_mixed_df, mode="automated")
        
        if result.statistics:
            stat = result.statistics[0]
            assert hasattr(stat, 'test_name')
            assert hasattr(stat, 'test_type')
            assert hasattr(stat, 'statistic')
            assert hasattr(stat, 'p_value')
            assert hasattr(stat, 'significant')
            assert hasattr(stat, 'interpretation')
    
    def test_json_output_structure(self, sample_mixed_df):
        """Test that JSON output has expected structure."""
        result = analyze(sample_mixed_df, mode="automated")
        output = result.to_dict()
        
        # Top-level keys
        assert 'summary' in output
        assert 'statistics' in output
        assert 'visualizations' in output
        assert 'insights' in output
        assert 'metadata' in output
        
        # Summary keys
        assert 'row_count' in output['summary']
        assert 'column_count' in output['summary']
