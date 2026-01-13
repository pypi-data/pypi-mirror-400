"""Feature detection module.

STANDALONE: All backend logic is copied here for PyPI distribution.
No external backend imports required.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np


@dataclass
class FeatureDetectionResult:
    """Result of feature detection."""
    column_roles: Dict[str, str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    identifier_columns: List[str]
    boolean_columns: List[str]
    groupable_columns: List[str]
    geo_latitude_columns: List[str] = field(default_factory=list)
    geo_longitude_columns: List[str] = field(default_factory=list)
    derived_features: List[Dict[str, Any]] = field(default_factory=list)


# =============================================================================
# COLUMN DETECTION HELPERS (from backend/analytics/analysis_policy.py)
# =============================================================================

def _is_latitude_column(col_lower: str, series: pd.Series) -> bool:
    """Check if column is a latitude coordinate.
    
    Detects latitude columns by name pattern and validates that values
    fall within the valid latitude range (-90 to 90 degrees).
    """
    lat_patterns = ['lat', 'latitude', '_lat', 'lat_']
    name_match = any(pat in col_lower for pat in lat_patterns)
    if not name_match:
        return False
    
    valid_data = series.dropna()
    if len(valid_data) == 0:
        return False
    
    try:
        min_val, max_val = valid_data.min(), valid_data.max()
        return bool(min_val >= -90 and max_val <= 90)
    except Exception:
        return False


def _is_longitude_column(col_lower: str, series: pd.Series) -> bool:
    """Check if column is a longitude coordinate.
    
    Detects longitude columns by name pattern and validates that values
    fall within the valid longitude range (-180 to 180 degrees).
    """
    lon_patterns = ['lon', 'lng', 'longitude', '_lon', '_lng', 'lon_', 'lng_']
    name_match = any(pat in col_lower for pat in lon_patterns)
    if not name_match:
        return False
    
    valid_data = series.dropna()
    if len(valid_data) == 0:
        return False
    
    try:
        min_val, max_val = valid_data.min(), valid_data.max()
        return bool(min_val >= -180 and max_val <= 180)
    except Exception:
        return False


def _is_numeric_id_column(col_lower: str, series: pd.Series, total_rows: int) -> bool:
    """Check if numeric column is an ID/identifier.
    
    Detects ID columns by name pattern (contains 'id', 'uuid', 'guid', etc.)
    and high uniqueness ratio (>=95% unique values).
    """
    id_patterns = ['_id', 'id_', 'uuid', 'guid', 'key_', '_key']
    name_ends_with_id = col_lower.endswith('id') and len(col_lower) > 2
    name_starts_with_id = (col_lower.startswith('id') and len(col_lower) > 2 and 
                           (col_lower[2] == '_' or col_lower[2].isdigit()))
    
    name_match = (any(pat in col_lower for pat in id_patterns) or 
                  name_ends_with_id or name_starts_with_id)
    
    if not name_match:
        return False
    
    try:
        unique_count = series.nunique(dropna=False)
        uniqueness_ratio = unique_count / total_rows if total_rows > 0 else 0
        return bool(uniqueness_ratio >= 0.95)
    except Exception:
        return False


# =============================================================================
# MAIN CLASSIFICATION FUNCTION (from backend/analytics/analysis_policy.py)
# =============================================================================

def classify_columns(df: pd.DataFrame) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    """Classify each column into exactly one role.
    
    Returns a tuple of (column_roles, derived_features).
    column_roles: mapping column_name -> one of:
        - 'identifier': unique ID columns (string or numeric)
        - 'measure': numeric columns suitable for statistical analysis
        - 'dimension': categorical columns for grouping
        - 'datetime': date/time columns
        - 'boolean': true/false columns
        - 'geo_latitude': latitude coordinate columns
        - 'geo_longitude': longitude coordinate columns
    derived_features: initially empty list
    
    Note: Columns classified as 'identifier', 'geo_latitude', or 'geo_longitude' 
    should be excluded from statistical analysis.
    """
    rows = len(df)
    roles: Dict[str, str] = {}
    derived: List[Dict[str, Any]] = []
    
    for col in df.columns:
        ser = df[col]
        dtype = str(ser.dtype)
        col_lower = col.lower()
        
        # Boolean detection
        if pd.api.types.is_bool_dtype(ser) or dtype == 'bool':
            roles[col] = 'boolean'
            continue
        
        # Datetime detection
        if pd.api.types.is_datetime64_any_dtype(ser) or pd.api.types.is_datetime64_dtype(ser):
            roles[col] = 'datetime'
            continue
        
        # Numeric columns: check for special types BEFORE classifying as measure
        if pd.api.types.is_numeric_dtype(ser):
            # Check for latitude coordinates
            if _is_latitude_column(col_lower, ser):
                roles[col] = 'geo_latitude'
                continue
            
            # Check for longitude coordinates
            if _is_longitude_column(col_lower, ser):
                roles[col] = 'geo_longitude'
                continue
            
            # Check for numeric ID columns
            if _is_numeric_id_column(col_lower, ser, rows):
                roles[col] = 'identifier'
                continue
            
            # Regular numeric column -> measure
            roles[col] = 'measure'
            continue
        
        # Strings/categorical -> candidate for identifier or dimension
        unique = ser.nunique(dropna=False)
        try:
            uniqueness_ratio = (unique / rows) if rows > 0 else 0
        except Exception:
            uniqueness_ratio = 0
        
        if uniqueness_ratio >= 0.95:
            roles[col] = 'identifier'
        else:
            roles[col] = 'dimension'
    
    return roles, derived


def handle_datetimes(
    df: pd.DataFrame, 
    roles: Dict[str, str]
) -> Tuple[pd.DataFrame, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Parse and validate datetime columns.
    
    Returns (df_parsed, derived_features, issues).
    Derived features may include computed durations for recognized start/end pairs.
    """
    df2 = df.copy()
    derived: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []
    
    datetime_cols = [c for c, r in roles.items() if r == 'datetime']
    
    # Parse datetime columns
    for col in datetime_cols:
        try:
            df2[col] = pd.to_datetime(df2[col], errors='coerce')
        except Exception as exc:
            issues.append({
                "type": "datetime_parse_failed",
                "column": col,
                "error": str(exc)
            })
    
    # Compute derived metrics for datetime pairs
    if len(datetime_cols) >= 2:
        lowered = [c.lower() for c in datetime_cols]
        pairs = []
        
        if 'admit_date' in lowered and 'discharge_date' in lowered:
            a = datetime_cols[lowered.index('admit_date')]
            d = datetime_cols[lowered.index('discharge_date')]
            pairs.append((a, d, 'length_of_stay'))
        
        if 'start_date' in lowered and 'end_date' in lowered:
            a = datetime_cols[lowered.index('start_date')]
            d = datetime_cols[lowered.index('end_date')]
            pairs.append((a, d, 'duration'))
        
        # Generic: pair first two if no named pairs found
        if not pairs and len(datetime_cols) >= 2:
            pairs.append((
                datetime_cols[0], 
                datetime_cols[1], 
                f"delta_{datetime_cols[0]}_{datetime_cols[1]}"
            ))
        
        for start_col, end_col, name in pairs:
            try:
                dur = (df2[end_col] - df2[start_col])
                neg_mask = dur.dt.total_seconds() < 0
                n_neg = int(neg_mask.sum()) if hasattr(neg_mask, 'sum') else 0
                if n_neg > 0:
                    issues.append({
                        "type": "logical_inconsistency",
                        "message": f"{n_neg} rows have {end_col} earlier than {start_col}",
                        "start_col": start_col,
                        "end_col": end_col,
                        "count": n_neg,
                    })
                df2[name] = dur.dt.total_seconds() / 3600.0  # hours
                derived.append({"name": name, "source": [start_col, end_col], "units": "hours"})
            except Exception as exc:
                issues.append({
                    "type": "derive_failed", 
                    "message": str(exc), 
                    "start": start_col, 
                    "end": end_col
                })
    
    return df2, derived, issues


def run_data_quality_checks(df: pd.DataFrame, roles: Dict[str, str]) -> Dict[str, Any]:
    """Return a data quality report including missing, duplicates, ranges, and logical checks."""
    report: Dict[str, Any] = {}
    rows, cols = df.shape
    
    # Missing values per column
    missing = df.isnull().sum().to_dict()
    report['missing_counts'] = {k: int(v) for k, v in missing.items()}
    
    # Duplicate rows
    dup_count = int(df.duplicated().sum()) if rows > 0 else 0
    report['duplicate_rows'] = dup_count
    
    # Basic invalid ranges check for numeric columns
    invalid_ranges = {}
    for col, role in roles.items():
        if role == 'measure' and pd.api.types.is_numeric_dtype(df[col]):
            col_min = df[col].min(skipna=True)
            col_max = df[col].max(skipna=True)
            if pd.isna(col_min) or pd.isna(col_max):
                invalid_ranges[col] = 'missing_stats'
            elif col_min > col_max:
                invalid_ranges[col] = {'min': float(col_min), 'max': float(col_max)}
    report['invalid_ranges'] = invalid_ranges
    
    # Datetime logical checks
    datetime_issues = {}
    for col, role in roles.items():
        if role == 'datetime':
            nat_count = int(df[col].isna().sum())
            if nat_count > 0:
                datetime_issues[col] = {'nat_count': nat_count}
    report['datetime_issues'] = datetime_issues
    
    return report


# =============================================================================
# FEATURE DETECTOR CLASS
# =============================================================================

class FeatureDetector:
    """Feature detection engine - fully standalone."""
    
    CATEGORICAL_MAX_CARDINALITY = 50
    GROUPABLE_MIN_ROWS_PER_GROUP = 2
    
    def detect(self, df: pd.DataFrame) -> FeatureDetectionResult:
        """Detect features using classify_columns."""
        roles, derived = classify_columns(df)
        
        numeric_columns = []
        categorical_columns = []
        datetime_columns = []
        identifier_columns = []
        boolean_columns = []
        groupable_columns = []
        geo_latitude_columns = []
        geo_longitude_columns = []
        
        total_rows = len(df)
        
        for col, role in roles.items():
            if role == 'datetime':
                datetime_columns.append(col)
            elif role == 'boolean':
                boolean_columns.append(col)
            elif role == 'identifier':
                identifier_columns.append(col)
            elif role == 'measure':
                numeric_columns.append(col)
            elif role == 'dimension':
                categorical_columns.append(col)
                if self._is_groupable(df[col], total_rows):
                    groupable_columns.append(col)
            elif role == 'geo_latitude':
                geo_latitude_columns.append(col)
            elif role == 'geo_longitude':
                geo_longitude_columns.append(col)
        
        return FeatureDetectionResult(
            column_roles=roles,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            datetime_columns=datetime_columns,
            identifier_columns=identifier_columns,
            boolean_columns=boolean_columns,
            groupable_columns=groupable_columns,
            geo_latitude_columns=geo_latitude_columns,
            geo_longitude_columns=geo_longitude_columns,
            derived_features=derived,
        )
    
    def _is_groupable(self, series: pd.Series, total_rows: int) -> bool:
        unique_count = series.nunique(dropna=True)
        if unique_count > self.CATEGORICAL_MAX_CARDINALITY:
            return False
        if unique_count > 0 and total_rows / unique_count < self.GROUPABLE_MIN_ROWS_PER_GROUP:
            return False
        return True
    
    def get_analysis_columns(self, result: FeatureDetectionResult) -> Tuple[List[str], List[str]]:
        """Get columns suitable for statistical analysis."""
        excluded = (set(result.identifier_columns) | 
                    set(result.geo_latitude_columns) | 
                    set(result.geo_longitude_columns))
        return ([c for c in result.numeric_columns if c not in excluded],
                [c for c in result.categorical_columns if c not in excluded])
