"""Data ingestion and validation module.

Handles schema validation, type normalization, and row/column snapshots.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class IngestionResult:
    """Result of data ingestion."""
    data: pd.DataFrame
    row_count: int
    column_count: int
    column_dtypes: Dict[str, str]
    issues: List[Dict[str, Any]] = field(default_factory=list)


class DataIngestion:
    """Data ingestion and validation.
    
    Handles:
    - Schema validation
    - Type normalization
    - Row and column snapshot
    """
    
    def __init__(self):
        """Initialize data ingestion."""
        self._issues: List[Dict[str, Any]] = []
    
    def ingest(self, data: pd.DataFrame) -> IngestionResult:
        """Ingest and validate a DataFrame.
        
        Args:
            data: Input DataFrame
            
        Returns:
            IngestionResult with validated data and metadata
            
        Raises:
            ValueError: If data is invalid
        """
        self._issues = []
        
        # Validate input
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("data cannot be empty")
        
        # Make a copy to avoid modifying original
        df = data.copy()
        
        # Normalize types
        df = self._normalize_types(df)
        
        # Capture column dtypes
        column_dtypes = {col: str(df[col].dtype) for col in df.columns}
        
        return IngestionResult(
            data=df,
            row_count=len(df),
            column_count=len(df.columns),
            column_dtypes=column_dtypes,
            issues=self._issues,
        )
    
    def _normalize_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column types for consistent analysis.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with normalized types
        """
        for col in df.columns:
            # Try to convert object columns to more specific types
            if df[col].dtype == 'object':
                # Try datetime conversion
                try:
                    parsed = pd.to_datetime(df[col], errors='coerce')
                    if parsed.notna().sum() > len(df) * 0.5:  # >50% valid
                        df[col] = parsed
                        continue
                except Exception:
                    pass
                
                # Try numeric conversion
                try:
                    parsed = pd.to_numeric(df[col], errors='coerce')
                    if parsed.notna().sum() > len(df) * 0.5:  # >50% valid
                        df[col] = parsed
                        continue
                except Exception:
                    pass
            
            # Convert int64 to float64 if there are NaN values
            if pd.api.types.is_integer_dtype(df[col]) and df[col].isna().any():
                df[col] = df[col].astype('float64')
        
        return df
    
    def validate_columns(
        self,
        df: pd.DataFrame,
        required_columns: Optional[List[str]] = None,
        exclude_columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Validate and filter columns.
        
        Args:
            df: Input DataFrame
            required_columns: Columns that must be present
            exclude_columns: Columns to exclude
            
        Returns:
            Filtered DataFrame
            
        Raises:
            ValueError: If required columns are missing
        """
        if required_columns:
            missing = set(required_columns) - set(df.columns)
            if missing:
                raise ValueError(f"Required columns missing: {missing}")
        
        if exclude_columns:
            df = df.drop(columns=[c for c in exclude_columns if c in df.columns])
        
        return df
