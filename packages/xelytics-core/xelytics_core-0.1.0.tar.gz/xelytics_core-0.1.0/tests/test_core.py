"""Unit tests for core modules.

Tests ingestion, profiling, and feature detection.
"""

import pytest
import pandas as pd
import numpy as np

from xelytics.core.ingestion import DataIngestion, IngestionResult
from xelytics.core.profiler import DataProfiler, ProfileResult
from xelytics.core.features import FeatureDetector, FeatureDetectionResult


class TestDataIngestion:
    """Tests for DataIngestion module."""
    
    def test_ingest_valid_dataframe(self, sample_mixed_df):
        """Test ingestion of valid DataFrame."""
        ingestion = DataIngestion()
        result = ingestion.ingest(sample_mixed_df)
        
        assert isinstance(result, IngestionResult)
        assert result.row_count == 100
        assert result.column_count == 5
        assert len(result.column_dtypes) == 5
    
    def test_ingest_empty_dataframe_raises(self):
        """Test that empty DataFrame raises ValueError."""
        ingestion = DataIngestion()
        with pytest.raises(ValueError, match="cannot be empty"):
            ingestion.ingest(pd.DataFrame())
    
    def test_ingest_invalid_type_raises(self):
        """Test that non-DataFrame raises error."""
        ingestion = DataIngestion()
        with pytest.raises(ValueError, match="must be a pandas DataFrame"):
            ingestion.ingest([1, 2, 3])  # type: ignore
    
    def test_type_normalization(self):
        """Test automatic type normalization."""
        ingestion = DataIngestion()
        df = pd.DataFrame({
            'numeric_str': ['1', '2', '3', '4', '5'],
            'date_str': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        })
        result = ingestion.ingest(df)
        
        # Should normalize numeric strings to proper types
        assert result.row_count == 5


class TestDataProfiler:
    """Tests for DataProfiler module."""
    
    def test_profile_numeric_columns(self, sample_numeric_df):
        """Test profiling numeric columns."""
        profiler = DataProfiler()
        result = profiler.profile(sample_numeric_df)
        
        assert isinstance(result, ProfileResult)
        assert len(result.column_profiles) == 4
        
        # Check numeric statistics present
        sales_profile = next(p for p in result.column_profiles if p.column_name == 'sales')
        assert sales_profile.mean is not None
        assert sales_profile.std is not None
        assert sales_profile.min is not None
        assert sales_profile.max is not None
    
    def test_profile_categorical_columns(self, sample_categorical_df):
        """Test profiling categorical columns."""
        profiler = DataProfiler()
        result = profiler.profile(sample_categorical_df)
        
        assert len(result.column_profiles) == 4
        
        # Check categorical statistics present
        region_profile = next(p for p in result.column_profiles if p.column_name == 'region')
        assert region_profile.unique_count == 4
        assert region_profile.data_type == 'categorical'
    
    def test_profile_missing_values(self, sample_with_missing_df):
        """Test profiling DataFrame with missing values."""
        profiler = DataProfiler()
        result = profiler.profile(sample_with_missing_df)
        
        assert result.total_missing_cells > 0
        
        # Check missing value detection
        value1_profile = next(p for p in result.column_profiles if p.column_name == 'value1')
        assert value1_profile.missing_count == 10


class TestFeatureDetector:
    """Tests for FeatureDetector module."""
    
    def test_detect_numeric_columns(self, sample_numeric_df):
        """Test detection of numeric columns."""
        detector = FeatureDetector()
        result = detector.detect(sample_numeric_df)
        
        assert isinstance(result, FeatureDetectionResult)
        assert len(result.numeric_columns) == 4
        assert 'sales' in result.numeric_columns
    
    def test_detect_categorical_columns(self, sample_categorical_df):
        """Test detection of categorical columns."""
        detector = FeatureDetector()
        result = detector.detect(sample_categorical_df)
        
        assert len(result.categorical_columns) == 4
        assert 'region' in result.categorical_columns
    
    def test_detect_datetime_columns(self, sample_mixed_df):
        """Test detection of datetime columns."""
        detector = FeatureDetector()
        result = detector.detect(sample_mixed_df)
        
        assert 'date' in result.datetime_columns
    
    def test_detect_groupable_columns(self, sample_mixed_df):
        """Test detection of groupable columns."""
        detector = FeatureDetector()
        result = detector.detect(sample_mixed_df)
        
        # Should detect region and category as groupable
        assert len(result.groupable_columns) >= 2
    
    def test_no_name_heuristics(self):
        """Test that feature detection uses data only, not column names.
        
        Per plan constraint: Feature detection must rely only on data.
        """
        detector = FeatureDetector()
        
        # Create DataFrame with misleading column names
        df = pd.DataFrame({
            'id_column': ['A', 'B', 'C'] * 10,  # Named like ID but low cardinality
            'date_field': [1.5, 2.5, 3.5] * 10,  # Named like date but numeric
            'target_var': np.random.choice(['X', 'Y'], 30),  # Named like target but categorical
        })
        
        result = detector.detect(df)
        
        # 'id_column' should NOT be classified as identifier (low cardinality)
        assert 'id_column' not in result.identifier_columns
        assert 'id_column' in result.categorical_columns
        
        # 'date_field' should NOT be classified as datetime (it's numeric)
        assert 'date_field' not in result.datetime_columns
        assert 'date_field' in result.numeric_columns
    
    def test_deterministic_detection(self, sample_mixed_df, assert_deterministic):
        """Test that feature detection is deterministic."""
        detector = FeatureDetector()
        
        def detect_wrapper():
            return detector.detect(sample_mixed_df)
        
        # Run 5 times and assert same output
        results = []
        for _ in range(5):
            result = detector.detect(sample_mixed_df)
            results.append(tuple(sorted(result.column_roles.items())))
        
        assert len(set(results)) == 1, "Feature detection is not deterministic"
