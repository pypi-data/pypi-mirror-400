"""Output schemas for analysis results.

This is the output contract - FROZEN.
Changes require version bump per backward compatibility rules.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import json
from datetime import datetime


class TestType(str, Enum):
    """Types of statistical tests."""
    ANOVA_ONE_WAY = "anova_one_way"
    ANOVA_TWO_WAY = "anova_two_way"
    T_TEST_INDEPENDENT = "t_test_independent"
    T_TEST_PAIRED = "t_test_paired"
    CHI_SQUARE = "chi_square"
    CORRELATION_PEARSON = "correlation_pearson"
    CORRELATION_SPEARMAN = "correlation_spearman"
    REGRESSION_LINEAR = "regression_linear"
    MANN_WHITNEY = "mann_whitney"
    KRUSKAL_WALLIS = "kruskal_wallis"
    NORMALITY_SHAPIRO = "normality_shapiro"
    NORMALITY_KS = "normality_ks"


class InsightSeverity(str, Enum):
    """Severity levels for insights."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class EffectSize:
    """Effect size measurement."""
    measure_type: str  # "cohens_d", "eta_squared", "cramers_v", etc.
    value: float
    interpretation: str  # "small", "medium", "large"
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class AssumptionCheck:
    """Result of a statistical assumption check."""
    assumption_name: str
    is_met: bool
    test_statistic: Optional[float] = None
    p_value: Optional[float] = None
    interpretation: str = ""
    recommendation: str = ""


@dataclass
class StatisticalTestResult:
    """Result of a single statistical test.
    
    This is a core output type - changes require version bump.
    """
    test_name: str
    test_type: TestType
    statistic: float
    p_value: float
    significant: bool
    interpretation: str
    
    # Optional extended results
    effect_size: Optional[EffectSize] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    assumptions: List[AssumptionCheck] = field(default_factory=list)
    
    # Columns involved
    columns: List[str] = field(default_factory=list)
    
    # Decision metadata (why this test was chosen)
    decision_reason: str = ""
    fallback_from: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "test_name": self.test_name,
            "test_type": self.test_type.value if isinstance(self.test_type, Enum) else self.test_type,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "significant": self.significant,
            "interpretation": self.interpretation,
            "columns": self.columns,
            "decision_reason": self.decision_reason,
            "fallback_from": self.fallback_from,
        }
        
        if self.effect_size:
            result["effect_size"] = asdict(self.effect_size)
        if self.confidence_interval:
            result["confidence_interval"] = list(self.confidence_interval)
        if self.assumptions:
            result["assumptions"] = [asdict(a) for a in self.assumptions]
            
        return result


@dataclass
class VisualizationSpec:
    """Specification for a visualization (Plotly JSON schema).
    
    Library-agnostic but versioned. Spec changes require version bump.
    """
    chart_id: str
    chart_type: str  # "bar", "scatter", "histogram", "box", "heatmap", etc.
    title: str
    
    # Plotly-compatible spec
    plotly_spec: Dict[str, Any] = field(default_factory=dict)
    
    # Columns used
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    
    # Related statistical result (if any)
    related_test_name: Optional[str] = None
    
    # Schema version for frontend compatibility
    spec_version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "chart_id": self.chart_id,
            "chart_type": self.chart_type,
            "title": self.title,
            "plotly_spec": self.plotly_spec,
            "x_column": self.x_column,
            "y_column": self.y_column,
            "color_column": self.color_column,
            "related_test_name": self.related_test_name,
            "spec_version": self.spec_version,
        }


@dataclass
class Insight:
    """A single insight from the analysis.
    
    Rule-based insights are generated without LLM.
    LLM-enhanced insights are optional.
    """
    insight_id: str
    severity: InsightSeverity
    title: str
    description: str
    
    # Source of insight
    source: str  # "rule_based" or "llm_enhanced"
    
    # Related columns/tests
    related_columns: List[str] = field(default_factory=list)
    related_test_name: Optional[str] = None
    
    # Evidence
    supporting_statistics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "insight_id": self.insight_id,
            "severity": self.severity.value if isinstance(self.severity, Enum) else self.severity,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "related_columns": self.related_columns,
            "related_test_name": self.related_test_name,
            "supporting_statistics": self.supporting_statistics,
        }


@dataclass
class ColumnProfile:
    """Profile of a single column."""
    column_name: str
    data_type: str  # "numeric", "categorical", "datetime", "identifier"
    role: str  # "metric", "dimension", "identifier", "datetime", "target"
    
    # Statistics
    missing_count: int = 0
    missing_percentage: float = 0.0
    unique_count: int = 0
    cardinality_ratio: float = 0.0
    
    # Numeric-specific
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    median: Optional[float] = None
    
    # Categorical-specific
    mode: Optional[str] = None
    top_values: List[Tuple[str, int]] = field(default_factory=list)


@dataclass
class DatasetSummary:
    """Summary of the input dataset."""
    row_count: int
    column_count: int
    
    # Column classifications
    numeric_columns: List[str] = field(default_factory=list)
    categorical_columns: List[str] = field(default_factory=list)
    datetime_columns: List[str] = field(default_factory=list)
    identifier_columns: List[str] = field(default_factory=list)
    
    # Profiles
    column_profiles: List[ColumnProfile] = field(default_factory=list)
    
    # Data quality
    total_missing_cells: int = 0
    duplicate_row_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "numeric_columns": self.numeric_columns,
            "categorical_columns": self.categorical_columns,
            "datetime_columns": self.datetime_columns,
            "identifier_columns": self.identifier_columns,
            "column_profiles": [asdict(p) for p in self.column_profiles],
            "total_missing_cells": self.total_missing_cells,
            "duplicate_row_count": self.duplicate_row_count,
        }


@dataclass
class RunMetadata:
    """Metadata about the analysis run."""
    execution_time_ms: int
    package_version: str
    
    # Dataset info
    row_count: int
    column_count: int
    
    # Execution stats
    tests_executed: int
    tests_skipped: int
    visualizations_generated: int
    insights_generated: int
    
    # Timestamps
    started_at: str = ""
    completed_at: str = ""
    
    # Mode and config
    mode: str = "automated"
    llm_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class AnalysisResult:
    """Complete analysis result - the output contract.
    
    FROZEN: Changes require version bump per backward compatibility rules:
    - Adding optional fields: minor version bump
    - Removing fields: major version bump
    - Changing field types: major version bump
    """
    summary: DatasetSummary
    statistics: List[StatisticalTestResult]
    visualizations: List[VisualizationSpec]
    insights: List[Insight]
    metadata: RunMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "summary": self.summary.to_dict(),
            "statistics": [s.to_dict() for s in self.statistics],
            "visualizations": [v.to_dict() for v in self.visualizations],
            "insights": [i.to_dict() for i in self.insights],
            "metadata": self.metadata.to_dict(),
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Deserialize from dictionary."""
        # Reconstruct nested objects
        summary = DatasetSummary(
            row_count=data["summary"]["row_count"],
            column_count=data["summary"]["column_count"],
            numeric_columns=data["summary"].get("numeric_columns", []),
            categorical_columns=data["summary"].get("categorical_columns", []),
            datetime_columns=data["summary"].get("datetime_columns", []),
            identifier_columns=data["summary"].get("identifier_columns", []),
            total_missing_cells=data["summary"].get("total_missing_cells", 0),
            duplicate_row_count=data["summary"].get("duplicate_row_count", 0),
        )
        
        statistics = []
        for s in data.get("statistics", []):
            effect_size = None
            if s.get("effect_size"):
                effect_size = EffectSize(**s["effect_size"])
            
            assumptions = []
            for a in s.get("assumptions", []):
                assumptions.append(AssumptionCheck(**a))
            
            statistics.append(StatisticalTestResult(
                test_name=s["test_name"],
                test_type=TestType(s["test_type"]) if isinstance(s["test_type"], str) else s["test_type"],
                statistic=s["statistic"],
                p_value=s["p_value"],
                significant=s["significant"],
                interpretation=s["interpretation"],
                effect_size=effect_size,
                confidence_interval=tuple(s["confidence_interval"]) if s.get("confidence_interval") else None,
                assumptions=assumptions,
                columns=s.get("columns", []),
                decision_reason=s.get("decision_reason", ""),
                fallback_from=s.get("fallback_from"),
            ))
        
        visualizations = []
        for v in data.get("visualizations", []):
            visualizations.append(VisualizationSpec(**v))
        
        insights = []
        for i in data.get("insights", []):
            insights.append(Insight(
                insight_id=i["insight_id"],
                severity=InsightSeverity(i["severity"]) if isinstance(i["severity"], str) else i["severity"],
                title=i["title"],
                description=i["description"],
                source=i["source"],
                related_columns=i.get("related_columns", []),
                related_test_name=i.get("related_test_name"),
                supporting_statistics=i.get("supporting_statistics", {}),
            ))
        
        metadata = RunMetadata(**data["metadata"])
        
        return cls(
            summary=summary,
            statistics=statistics,
            visualizations=visualizations,
            insights=insights,
            metadata=metadata,
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AnalysisResult":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))
