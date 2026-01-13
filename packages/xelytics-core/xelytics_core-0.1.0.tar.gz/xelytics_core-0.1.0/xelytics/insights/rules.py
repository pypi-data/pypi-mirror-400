"""Rule-based insight generation.

Generates structured insights from analysis results.
No LLM - deterministic rules only.
"""

from dataclasses import dataclass
from typing import List, Optional
import uuid

from xelytics.schemas.outputs import (
    Insight,
    InsightSeverity,
    StatisticalTestResult,
    DatasetSummary,
)
from xelytics.core.profiler import ProfileResult


class InsightGenerator:
    """Rule-based insight generator.
    
    Generates insights from analysis results using deterministic rules.
    No LLM, no guessing.
    """
    
    def generate(
        self,
        summary: DatasetSummary,
        profile: ProfileResult,
        test_results: List[StatisticalTestResult],
        max_insights: int = 20,
    ) -> List[Insight]:
        """Generate insights from analysis results.
        
        Args:
            summary: Dataset summary
            profile: Profile result
            test_results: Statistical test results
            max_insights: Maximum number of insights
            
        Returns:
            List of Insight objects
        """
        insights = []
        
        # Data quality insights
        insights.extend(self._generate_quality_insights(summary, profile))
        
        # Statistical insights
        insights.extend(self._generate_statistical_insights(test_results))
        
        # Dataset overview insights
        insights.extend(self._generate_overview_insights(summary))
        
        return insights[:max_insights]
    
    def _generate_quality_insights(
        self,
        summary: DatasetSummary,
        profile: ProfileResult,
    ) -> List[Insight]:
        """Generate data quality insights."""
        insights = []
        
        # High missing data insight
        total_cells = summary.row_count * summary.column_count
        if total_cells > 0:
            missing_pct = (summary.total_missing_cells / total_cells) * 100
            if missing_pct > 10:
                insights.append(Insight(
                    insight_id=self._generate_id(),
                    severity=InsightSeverity.WARNING,
                    title="Significant Missing Data",
                    description=f"Dataset has {missing_pct:.1f}% missing values ({summary.total_missing_cells:,} cells). Consider imputation or removal strategies.",
                    source="rule_based",
                    supporting_statistics={
                        "missing_cells": summary.total_missing_cells,
                        "missing_percentage": missing_pct,
                    },
                ))
        
        # Duplicate rows insight
        if summary.duplicate_row_count > 0:
            dup_pct = (summary.duplicate_row_count / summary.row_count) * 100
            severity = InsightSeverity.WARNING if dup_pct > 5 else InsightSeverity.INFO
            insights.append(Insight(
                insight_id=self._generate_id(),
                severity=severity,
                title="Duplicate Rows Detected",
                description=f"Found {summary.duplicate_row_count:,} duplicate rows ({dup_pct:.1f}% of data).",
                source="rule_based",
                supporting_statistics={
                    "duplicate_count": summary.duplicate_row_count,
                    "duplicate_percentage": dup_pct,
                },
            ))
        
        # Column-specific quality issues
        for issue in profile.quality_issues:
            if issue.get("issue") == "high_missing":
                insights.append(Insight(
                    insight_id=self._generate_id(),
                    severity=InsightSeverity.WARNING,
                    title=f"High Missing Values in '{issue['column']}'",
                    description=f"Column '{issue['column']}' has {issue['percentage']:.1f}% missing values.",
                    source="rule_based",
                    related_columns=[issue['column']],
                    supporting_statistics={
                        "missing_percentage": issue['percentage'],
                    },
                ))
        
        return insights
    
    def _generate_statistical_insights(
        self,
        test_results: List[StatisticalTestResult],
    ) -> List[Insight]:
        """Generate insights from statistical test results."""
        insights = []
        
        for result in test_results:
            if result.significant:
                # Significant result insight
                severity = InsightSeverity.INFO
                if result.effect_size:
                    if result.effect_size.interpretation in ["large", "very strong"]:
                        severity = InsightSeverity.CRITICAL
                
                insights.append(Insight(
                    insight_id=self._generate_id(),
                    severity=severity,
                    title=f"Significant Finding: {result.test_name}",
                    description=result.interpretation,
                    source="rule_based",
                    related_columns=result.columns,
                    related_test_name=result.test_name,
                    supporting_statistics={
                        "p_value": result.p_value,
                        "statistic": result.statistic,
                        "effect_size": result.effect_size.value if result.effect_size else None,
                    },
                ))
        
        # Summary insights
        significant_count = sum(1 for r in test_results if r.significant)
        if len(test_results) > 0:
            insights.append(Insight(
                insight_id=self._generate_id(),
                severity=InsightSeverity.INFO,
                title="Statistical Analysis Summary",
                description=f"Found {significant_count} significant relationships out of {len(test_results)} tests conducted.",
                source="rule_based",
                supporting_statistics={
                    "significant_count": significant_count,
                    "total_tests": len(test_results),
                    "significance_rate": significant_count / len(test_results),
                },
            ))
        
        return insights
    
    def _generate_overview_insights(
        self,
        summary: DatasetSummary,
    ) -> List[Insight]:
        """Generate dataset overview insights."""
        insights = []
        
        # Dataset size insight
        insights.append(Insight(
            insight_id=self._generate_id(),
            severity=InsightSeverity.INFO,
            title="Dataset Overview",
            description=f"Analyzed {summary.row_count:,} rows across {summary.column_count} columns: {len(summary.numeric_columns)} numeric, {len(summary.categorical_columns)} categorical.",
            source="rule_based",
            supporting_statistics={
                "row_count": summary.row_count,
                "column_count": summary.column_count,
                "numeric_columns": len(summary.numeric_columns),
                "categorical_columns": len(summary.categorical_columns),
            },
        ))
        
        # Small sample warning
        if summary.row_count < 30:
            insights.append(Insight(
                insight_id=self._generate_id(),
                severity=InsightSeverity.WARNING,
                title="Small Sample Size",
                description=f"Dataset has only {summary.row_count} rows. Statistical results may not be reliable.",
                source="rule_based",
                supporting_statistics={
                    "row_count": summary.row_count,
                },
            ))
        
        return insights
    
    def _generate_id(self) -> str:
        """Generate unique insight ID."""
        return str(uuid.uuid4())[:8]
