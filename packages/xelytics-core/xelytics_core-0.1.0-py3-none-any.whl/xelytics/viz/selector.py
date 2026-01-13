"""Chart selector module.

Selects appropriate chart types based on data characteristics.
Uses deterministic rules - no LLM.
"""

from typing import List, Optional, Tuple
import pandas as pd

from xelytics.core.features import FeatureDetectionResult


class ChartSelector:
    """Chart type selector.
    
    Deterministic chart selection based on data characteristics.
    No LLM, no guessing.
    """
    
    # Chart type configurations
    CHART_TYPES = {
        "histogram": {"min_data": 10, "max_categories": None},
        "bar": {"min_data": 2, "max_categories": 20},
        "scatter": {"min_data": 10, "max_categories": None},
        "box": {"min_data": 5, "max_categories": 10},
        "heatmap": {"min_data": 10, "max_categories": 20},
        "pie": {"min_data": 2, "max_categories": 8},
        "line": {"min_data": 5, "max_categories": None},
    }
    
    def select_charts(
        self,
        df: pd.DataFrame,
        features: FeatureDetectionResult,
        max_charts: int = 10,
    ) -> List[dict]:
        """Select appropriate charts for the data.
        
        Args:
            df: Input DataFrame
            features: Feature detection result
            max_charts: Maximum number of charts
            
        Returns:
            List of chart specifications
        """
        charts = []
        
        # Histograms for numeric columns
        for col in features.numeric_columns[:3]:
            if len(df[col].dropna()) >= 10:
                charts.append({
                    "chart_type": "histogram",
                    "x_column": col,
                    "title": f"Distribution of {col}",
                })
        
        # Bar charts for categorical columns
        for col in features.categorical_columns[:3]:
            n_categories = df[col].nunique()
            if 2 <= n_categories <= 20:
                charts.append({
                    "chart_type": "bar",
                    "x_column": col,
                    "title": f"Count by {col}",
                })
        
        # Scatter plots for numeric pairs
        numeric = features.numeric_columns[:4]
        for i, col1 in enumerate(numeric):
            for col2 in numeric[i+1:]:
                if len(charts) >= max_charts:
                    break
                charts.append({
                    "chart_type": "scatter",
                    "x_column": col1,
                    "y_column": col2,
                    "title": f"{col1} vs {col2}",
                })
        
        # Box plots for numeric by categorical
        if features.numeric_columns and features.groupable_columns:
            num_col = features.numeric_columns[0]
            group_col = features.groupable_columns[0]
            n_groups = df[group_col].nunique()
            if 2 <= n_groups <= 10:
                charts.append({
                    "chart_type": "box",
                    "x_column": group_col,
                    "y_column": num_col,
                    "title": f"{num_col} by {group_col}",
                })
        
        return charts[:max_charts]
    
    def select_for_test_result(
        self,
        test_type: str,
        columns: List[str],
        df: pd.DataFrame,
    ) -> Optional[dict]:
        """Select chart type for a statistical test result.
        
        Args:
            test_type: Type of statistical test
            columns: Columns involved
            df: Data
            
        Returns:
            Chart specification or None
        """
        if test_type in ["t_test", "anova"]:
            if len(columns) >= 2:
                return {
                    "chart_type": "box",
                    "x_column": columns[1],  # Group column
                    "y_column": columns[0],  # Value column
                    "title": f"{columns[0]} by {columns[1]}",
                }
        
        elif test_type == "chi_square":
            if len(columns) >= 2:
                return {
                    "chart_type": "heatmap",
                    "x_column": columns[0],
                    "y_column": columns[1],
                    "title": f"Association: {columns[0]} vs {columns[1]}",
                }
        
        elif test_type == "correlation":
            if len(columns) >= 2:
                return {
                    "chart_type": "scatter",
                    "x_column": columns[0],
                    "y_column": columns[1],
                    "title": f"Correlation: {columns[0]} vs {columns[1]}",
                }
        
        elif test_type == "normality":
            if len(columns) >= 1:
                return {
                    "chart_type": "histogram",
                    "x_column": columns[0],
                    "title": f"Distribution of {columns[0]}",
                }
        
        return None
