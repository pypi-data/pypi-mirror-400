"""Insight narrator using LLM.

Enhances rule-based insights with natural language narration.
LLM is for narration ONLY - does not change analytics results.
"""

from typing import List, Optional

from xelytics.schemas.outputs import AnalysisResult, Insight, InsightSeverity
from xelytics.llm.provider import LLMProvider, NoOpProvider


class InsightNarrator:
    """LLM-based insight narrator.
    
    Enhances insights with natural language explanations.
    
    Strict Guardrails:
    - Input: structured results only
    - Output: text only
    - Does NOT change analytics results
    - Disabling LLM does NOT affect other results
    """
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """Initialize narrator.
        
        Args:
            provider: LLM provider to use. If None, uses NoOpProvider.
        """
        self.provider = provider or NoOpProvider()
    
    def narrate(self, result: AnalysisResult) -> str:
        """Generate narrative summary of analysis results.
        
        Args:
            result: Analysis result to narrate
            
        Returns:
            Natural language summary
        """
        if isinstance(self.provider, NoOpProvider):
            return self._generate_rule_based_narrative(result)
        
        # Build context for LLM
        context = self._build_context(result)
        
        system_prompt = """You are a data analyst assistant. 
Generate a clear, concise summary of the statistical analysis results.
Focus on key findings, significant patterns, and actionable insights.
Use plain language, avoid jargon."""
        
        user_prompt = f"""Summarize these analysis results:

Dataset: {result.metadata.row_count} rows, {result.metadata.column_count} columns

Key Findings:
{context}

Provide a 2-3 paragraph summary suitable for a business audience."""
        
        llm_result = self.provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=512,
            temperature=0.5,
        )
        
        if llm_result.content and not llm_result.content.startswith("Error:"):
            return llm_result.content
        
        # Fallback to rule-based
        return self._generate_rule_based_narrative(result)
    
    def enhance_insights(
        self,
        insights: List[Insight],
    ) -> List[Insight]:
        """Enhance insights with LLM-generated descriptions.
        
        Args:
            insights: List of rule-based insights
            
        Returns:
            Same insights, potentially with enhanced descriptions
        """
        if isinstance(self.provider, NoOpProvider):
            return insights
        
        # For now, return insights unchanged
        # LLM enhancement can be added later without changing analytics
        return insights
    
    def _build_context(self, result: AnalysisResult) -> str:
        """Build context string from analysis result."""
        lines = []
        
        # Add significant findings
        significant = [s for s in result.statistics if s.significant]
        if significant:
            lines.append(f"Found {len(significant)} significant statistical relationships:")
            for s in significant[:5]:
                lines.append(f"  - {s.interpretation}")
        
        # Add key insights
        if result.insights:
            lines.append(f"\nTop insights:")
            for insight in result.insights[:5]:
                lines.append(f"  - [{insight.severity.value}] {insight.title}: {insight.description}")
        
        return "\n".join(lines)
    
    def _generate_rule_based_narrative(self, result: AnalysisResult) -> str:
        """Generate narrative using rules only (no LLM)."""
        lines = []
        
        # Overview
        lines.append(f"Analysis of {result.metadata.row_count:,} records across {result.metadata.column_count} columns completed in {result.metadata.execution_time_ms}ms.")
        
        # Statistical summary
        significant = [s for s in result.statistics if s.significant]
        if significant:
            lines.append(f"\nFound {len(significant)} significant findings:")
            for s in significant[:3]:
                lines.append(f"• {s.interpretation}")
        else:
            lines.append("\nNo statistically significant relationships detected.")
        
        # Data quality
        if result.summary.total_missing_cells > 0:
            total_cells = result.summary.row_count * result.summary.column_count
            missing_pct = (result.summary.total_missing_cells / total_cells) * 100
            lines.append(f"\nData quality note: {missing_pct:.1f}% missing values detected.")
        
        return "\n".join(lines)
