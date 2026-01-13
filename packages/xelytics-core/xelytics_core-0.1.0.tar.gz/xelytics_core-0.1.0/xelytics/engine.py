"""Main analysis engine.

The public API entry point: analyze()
"""

from typing import Literal, Optional
import time
import pandas as pd

from xelytics.__version__ import __version__
from xelytics.schemas.config import AnalysisConfig
from xelytics.schemas.outputs import (
    AnalysisResult,
    DatasetSummary,
    RunMetadata,
)
from xelytics.core.ingestion import DataIngestion
from xelytics.core.profiler import DataProfiler
from xelytics.core.features import FeatureDetector
from xelytics.stats.engine import StatisticalEngine
from xelytics.viz.generator import VisualizationGenerator
from xelytics.insights.rules import InsightGenerator


def analyze(
    data: pd.DataFrame,
    mode: Literal["automated", "semi-automated"] = "automated",
    config: Optional[AnalysisConfig] = None,
) -> AnalysisResult:
    """Analyze a dataset and return comprehensive results.
    
    This is the public API entry point.
    
    Args:
        data: Input DataFrame to analyze
        mode: Analysis mode ("automated" or "semi-automated")
        config: Optional configuration. Uses defaults if not provided.
        
    Returns:
        AnalysisResult with summary, statistics, visualizations, and insights.
        
    Raises:
        ValueError: If data is invalid
        XelyticsError: If analysis fails
        
    Example:
        >>> from xelytics import analyze, AnalysisConfig
        >>> import pandas as pd
        >>> 
        >>> df = pd.read_csv("data.csv")
        >>> result = analyze(df, mode="automated")
        >>> print(result.to_json())
    """
    start_time = time.time()
    
    # Use default config if not provided
    if config is None:
        config = AnalysisConfig(mode=mode)
    else:
        config.mode = mode
    
    # Filter columns if specified
    if config.include_columns:
        data = data[[c for c in config.include_columns if c in data.columns]]
    if config.exclude_columns:
        data = data.drop(columns=[c for c in config.exclude_columns if c in data.columns])
    
    # Step 1: Ingestion & Validation
    ingestion = DataIngestion()
    ingestion_result = ingestion.ingest(data)
    df = ingestion_result.data
    
    # Step 2: Feature Detection
    feature_detector = FeatureDetector()
    features = feature_detector.detect(df)
    
    # Step 3: Data Profiling
    profiler = DataProfiler()
    profile = profiler.profile(df, features.column_roles)
    
    # Step 4: Statistical Analysis
    stats_engine = StatisticalEngine(alpha=config.significance_level)
    stats_result = stats_engine.execute(df, features)
    
    # Step 5: Visualization Generation
    viz_generator = VisualizationGenerator()
    visualizations = viz_generator.generate(
        df,
        features,
        stats_result.results,
        max_visualizations=config.max_visualizations,
    )
    
    # Step 6: Build Dataset Summary
    summary = DatasetSummary(
        row_count=ingestion_result.row_count,
        column_count=ingestion_result.column_count,
        numeric_columns=features.numeric_columns,
        categorical_columns=features.categorical_columns,
        datetime_columns=features.datetime_columns,
        identifier_columns=features.identifier_columns,
        column_profiles=profile.column_profiles,
        total_missing_cells=profile.total_missing_cells,
        duplicate_row_count=profile.duplicate_row_count,
    )
    
    # Step 7: Generate Insights (rule-based)
    insight_generator = InsightGenerator()
    insights = insight_generator.generate(
        summary,
        profile,
        stats_result.results,
        max_insights=config.max_insights,
    )
    
    # Step 8: Build Metadata
    execution_time_ms = int((time.time() - start_time) * 1000)
    
    metadata = RunMetadata(
        execution_time_ms=execution_time_ms,
        package_version=__version__,
        row_count=ingestion_result.row_count,
        column_count=ingestion_result.column_count,
        tests_executed=stats_result.tests_executed,
        tests_skipped=stats_result.tests_failed,
        visualizations_generated=len(visualizations),
        insights_generated=len(insights),
        mode=config.mode,
        llm_enabled=config.enable_llm_insights,
    )
    
    # Step 9: Assemble Final Result
    return AnalysisResult(
        summary=summary,
        statistics=stats_result.results,
        visualizations=visualizations,
        insights=insights,
        metadata=metadata,
    )
