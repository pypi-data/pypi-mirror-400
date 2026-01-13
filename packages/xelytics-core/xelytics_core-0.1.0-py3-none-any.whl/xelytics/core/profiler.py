"""Data profiling module.

Generates statistical profiles for each column:
- Missing values detection
- Cardinality calculation
- Basic distributions
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from xelytics.schemas.outputs import ColumnProfile


@dataclass
class ProfileResult:
    """Result of data profiling."""
    column_profiles: List[ColumnProfile]
    total_missing_cells: int
    duplicate_row_count: int
    quality_issues: List[Dict[str, Any]] = field(default_factory=list)


class DataProfiler:
    """Data profiling engine.
    
    Computes statistics for each column:
    - Missing values
    - Cardinality
    - Distributions
    
    Uses DATA ONLY for profiling - no name-based heuristics.
    """
    
    def profile(
        self,
        df: pd.DataFrame,
        column_roles: Optional[Dict[str, str]] = None,
    ) -> ProfileResult:
        """Profile a DataFrame.
        
        Args:
            df: Input DataFrame
            column_roles: Optional pre-computed column roles
            
        Returns:
            ProfileResult with column profiles and quality metrics
        """
        profiles = []
        quality_issues = []
        
        for col in df.columns:
            series = df[col]
            role = column_roles.get(col, "unknown") if column_roles else "unknown"
            
            profile = self._profile_column(col, series, role)
            profiles.append(profile)
            
            # Check for quality issues
            if profile.missing_percentage > 50:
                quality_issues.append({
                    "column": col,
                    "issue": "high_missing",
                    "severity": "warning",
                    "percentage": profile.missing_percentage,
                })
        
        # Calculate total missing cells
        total_missing = sum(p.missing_count for p in profiles)
        
        # Count duplicate rows
        duplicate_count = int(df.duplicated().sum())
        
        return ProfileResult(
            column_profiles=profiles,
            total_missing_cells=total_missing,
            duplicate_row_count=duplicate_count,
            quality_issues=quality_issues,
        )
    
    def _profile_column(
        self,
        col_name: str,
        series: pd.Series,
        role: str,
    ) -> ColumnProfile:
        """Profile a single column.
        
        Args:
            col_name: Column name
            series: Column data
            role: Column role (metric, dimension, etc.)
            
        Returns:
            ColumnProfile with statistics
        """
        # Determine data type based on actual data (not column name)
        data_type = self._detect_data_type(series)
        
        # Basic statistics
        total = len(series)
        missing_count = int(series.isna().sum())
        missing_percentage = (missing_count / total * 100) if total > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))
        cardinality_ratio = (unique_count / total) if total > 0 else 0.0
        
        profile = ColumnProfile(
            column_name=col_name,
            data_type=data_type,
            role=role,
            missing_count=missing_count,
            missing_percentage=missing_percentage,
            unique_count=unique_count,
            cardinality_ratio=cardinality_ratio,
        )
        
        # Add numeric statistics if applicable
        if data_type == "numeric":
            valid_data = series.dropna()
            if len(valid_data) > 0:
                profile.mean = float(valid_data.mean())
                profile.std = float(valid_data.std())
                profile.min = float(valid_data.min())
                profile.max = float(valid_data.max())
                profile.median = float(valid_data.median())
        
        # Add categorical statistics if applicable
        if data_type == "categorical":
            mode_result = series.mode()
            if len(mode_result) > 0:
                profile.mode = str(mode_result.iloc[0])
            
            # Top values
            value_counts = series.value_counts().head(5)
            profile.top_values = [
                (str(val), int(count))
                for val, count in value_counts.items()
            ]
        
        return profile
    
    def _detect_data_type(self, series: pd.Series) -> str:
        """Detect column data type from data (not column name).
        
        Args:
            series: Column data
            
        Returns:
            One of: "numeric", "categorical", "datetime", "identifier", "boolean"
        """
        dtype = series.dtype
        
        # Boolean
        if pd.api.types.is_bool_dtype(dtype):
            return "boolean"
        
        # Datetime
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "datetime"
        
        # Numeric
        if pd.api.types.is_numeric_dtype(dtype):
            return "numeric"
        
        # Check if high cardinality suggests identifier (based on DATA, not name)
        total = len(series)
        unique = series.nunique(dropna=True)
        if total > 0 and unique / total >= 0.95:
            return "identifier"
        
        # Default to categorical
        return "categorical"
