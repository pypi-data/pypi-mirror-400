"""Visualization generator module.

Generates Plotly-compatible visualization specs.
Versioned schema for frontend stability.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
import uuid

from xelytics.schemas.outputs import VisualizationSpec, StatisticalTestResult
from xelytics.core.features import FeatureDetectionResult
from xelytics.viz.selector import ChartSelector


# Schema version - changes require version bump
VISUALIZATION_SPEC_VERSION = "1.0"


class VisualizationGenerator:
    """Visualization spec generator.
    
    Generates Plotly-compatible JSON specs.
    
    Stability Rule:
    - Visualization spec schema is versioned
    - Spec changes cannot break frontend without version bump
    """
    
    def __init__(self):
        """Initialize visualization generator."""
        self.selector = ChartSelector()
    
    def generate(
        self,
        df: pd.DataFrame,
        features: FeatureDetectionResult,
        test_results: Optional[List[StatisticalTestResult]] = None,
        max_visualizations: int = 10,
    ) -> List[VisualizationSpec]:
        """Generate visualization specs for the data.
        
        Args:
            df: Input DataFrame
            features: Feature detection result
            test_results: Optional statistical test results
            max_visualizations: Maximum number of visualizations
            
        Returns:
            List of VisualizationSpec objects
        """
        visualizations = []
        
        # Select charts based on data
        chart_specs = self.selector.select_charts(df, features, max_visualizations)
        
        for spec in chart_specs:
            vis = self._create_visualization(df, spec)
            if vis:
                visualizations.append(vis)
        
        # Add visualizations for test results
        if test_results:
            for result in test_results:
                if len(visualizations) >= max_visualizations:
                    break
                
                chart_spec = self.selector.select_for_test_result(
                    result.test_type.value if hasattr(result.test_type, 'value') else result.test_type,
                    result.columns,
                    df,
                )
                if chart_spec:
                    chart_spec["related_test_name"] = result.test_name
                    vis = self._create_visualization(df, chart_spec)
                    if vis:
                        visualizations.append(vis)
        
        return visualizations[:max_visualizations]
    
    def _create_visualization(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> Optional[VisualizationSpec]:
        """Create a visualization spec from chart specification.
        
        Args:
            df: Data
            spec: Chart specification
            
        Returns:
            VisualizationSpec or None
        """
        chart_type = spec.get("chart_type")
        
        try:
            if chart_type == "histogram":
                plotly_spec = self._create_histogram(df, spec)
            elif chart_type == "bar":
                plotly_spec = self._create_bar(df, spec)
            elif chart_type == "scatter":
                plotly_spec = self._create_scatter(df, spec)
            elif chart_type == "box":
                plotly_spec = self._create_box(df, spec)
            elif chart_type == "heatmap":
                plotly_spec = self._create_heatmap(df, spec)
            else:
                return None
            
            return VisualizationSpec(
                chart_id=str(uuid.uuid4())[:8],
                chart_type=chart_type,
                title=spec.get("title", f"{chart_type} chart"),
                plotly_spec=plotly_spec,
                x_column=spec.get("x_column"),
                y_column=spec.get("y_column"),
                color_column=spec.get("color_column"),
                related_test_name=spec.get("related_test_name"),
                spec_version=VISUALIZATION_SPEC_VERSION,
            )
        except Exception:
            return None
    
    def _create_histogram(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create histogram Plotly spec."""
        x_col = spec["x_column"]
        values = df[x_col].dropna().tolist()
        
        return {
            "data": [{
                "type": "histogram",
                "x": values,
                "name": x_col,
            }],
            "layout": {
                "title": spec.get("title", f"Distribution of {x_col}"),
                "xaxis": {"title": x_col},
                "yaxis": {"title": "Count"},
            }
        }
    
    def _create_bar(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create bar chart Plotly spec."""
        x_col = spec["x_column"]
        value_counts = df[x_col].value_counts()
        
        return {
            "data": [{
                "type": "bar",
                "x": value_counts.index.tolist(),
                "y": value_counts.values.tolist(),
                "name": x_col,
            }],
            "layout": {
                "title": spec.get("title", f"Count by {x_col}"),
                "xaxis": {"title": x_col},
                "yaxis": {"title": "Count"},
            }
        }
    
    def _create_scatter(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create scatter plot Plotly spec."""
        x_col = spec["x_column"]
        y_col = spec["y_column"]
        
        clean_data = df[[x_col, y_col]].dropna()
        
        return {
            "data": [{
                "type": "scatter",
                "mode": "markers",
                "x": clean_data[x_col].tolist(),
                "y": clean_data[y_col].tolist(),
                "name": f"{x_col} vs {y_col}",
            }],
            "layout": {
                "title": spec.get("title", f"{x_col} vs {y_col}"),
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
            }
        }
    
    def _create_box(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create box plot Plotly spec."""
        x_col = spec["x_column"]
        y_col = spec["y_column"]
        
        traces = []
        for group_name, group_data in df.groupby(x_col):
            traces.append({
                "type": "box",
                "y": group_data[y_col].dropna().tolist(),
                "name": str(group_name),
            })
        
        return {
            "data": traces,
            "layout": {
                "title": spec.get("title", f"{y_col} by {x_col}"),
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
            }
        }
    
    def _create_heatmap(
        self,
        df: pd.DataFrame,
        spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create heatmap Plotly spec."""
        x_col = spec["x_column"]
        y_col = spec["y_column"]
        
        # Create crosstab
        crosstab = pd.crosstab(df[y_col], df[x_col])
        
        return {
            "data": [{
                "type": "heatmap",
                "z": crosstab.values.tolist(),
                "x": crosstab.columns.tolist(),
                "y": crosstab.index.tolist(),
                "colorscale": "Viridis",
            }],
            "layout": {
                "title": spec.get("title", f"{x_col} vs {y_col}"),
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
            }
        }
