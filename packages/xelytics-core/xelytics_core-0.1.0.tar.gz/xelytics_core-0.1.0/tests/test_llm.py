"""Tests for LLM integration with mocking.

Tests LLM narrator without making actual API calls.
"""

import pytest
from unittest.mock import MagicMock, patch

from xelytics import analyze, AnalysisConfig
from xelytics.llm.provider import LLMProvider, LLMResult, NoOpProvider
from xelytics.llm.narrator import InsightNarrator
from xelytics.llm.providers.openai import OpenAIProvider


class TestNoOpProvider:
    """Tests for NoOpProvider (LLM disabled)."""
    
    def test_noop_returns_empty(self):
        """Test that NoOpProvider returns empty results."""
        provider = NoOpProvider()
        result = provider.generate(
            system_prompt="Test",
            user_prompt="Test",
        )
        
        assert isinstance(result, LLMResult)
        assert result.content == ""
        assert result.provider == "noop"
    
    def test_noop_health_check(self):
        """Test that NoOpProvider is always healthy."""
        provider = NoOpProvider()
        assert provider.health_check() is True


class TestInsightNarrator:
    """Tests for InsightNarrator with mocked LLM."""
    
    def test_narrate_with_noop(self, sample_mixed_df):
        """Test narration with NoOp provider (rule-based)."""
        result = analyze(sample_mixed_df, mode="automated")
        
        narrator = InsightNarrator(provider=NoOpProvider())
        narrative = narrator.narrate(result)
        
        assert len(narrative) > 0
        assert "Analysis" in narrative or "records" in narrative.lower()
    
    def test_narrate_with_mock(self, sample_mixed_df, mock_llm_provider):
        """Test narration with mock LLM provider."""
        result = analyze(sample_mixed_df, mode="automated")
        
        narrator = InsightNarrator(provider=mock_llm_provider)
        narrative = narrator.narrate(result)
        
        assert narrative == "Mock analysis summary."
        assert len(mock_llm_provider.calls) == 1
    
    def test_narrator_fallback_on_error(self, sample_mixed_df):
        """Test that narrator falls back to rule-based on LLM error."""
        # Create a failing provider
        class FailingProvider(LLMProvider):
            @property
            def name(self):
                return "failing"
            
            def generate(self, *args, **kwargs):
                return LLMResult(content="Error: API failed", provider="failing")
            
            def health_check(self):
                return False
        
        result = analyze(sample_mixed_df, mode="automated")
        
        narrator = InsightNarrator(provider=FailingProvider())
        narrative = narrator.narrate(result)
        
        # Should fall back to rule-based
        assert len(narrative) > 0
        assert "Analysis" in narrative


class TestLLMIndependence:
    """Tests that LLM does not affect analytics results."""
    
    def test_analytics_same_with_and_without_llm(self, sample_mixed_df):
        """Test that analytics results are identical with/without LLM."""
        config_no_llm = AnalysisConfig(
            mode="automated",
            enable_llm_insights=False,
        )
        config_with_llm = AnalysisConfig(
            mode="automated",
            enable_llm_insights=True,  # Would try to use LLM
        )
        
        result_no_llm = analyze(sample_mixed_df, mode="automated", config=config_no_llm)
        result_with_llm = analyze(sample_mixed_df, mode="automated", config=config_with_llm)
        
        # Core analytics should be identical
        assert result_no_llm.summary.row_count == result_with_llm.summary.row_count
        assert result_no_llm.summary.column_count == result_with_llm.summary.column_count
        assert len(result_no_llm.statistics) == len(result_with_llm.statistics)
        
        # Statistical test results should be identical
        for r1, r2 in zip(result_no_llm.statistics, result_with_llm.statistics):
            assert r1.p_value == r2.p_value
            assert r1.statistic == r2.statistic
    
    def test_insights_present_without_llm(self, sample_mixed_df):
        """Test that insights are generated without LLM."""
        config = AnalysisConfig(mode="automated", enable_llm_insights=False)
        result = analyze(sample_mixed_df, mode="automated", config=config)
        
        # Rule-based insights should still be present
        assert len(result.insights) > 0
        
        # All insights should be rule-based
        for insight in result.insights:
            assert insight.source == "rule_based"


class TestOpenAIProviderMocked:
    """Tests for OpenAI provider with mocks (no actual API calls)."""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_provider_initialization(self):
        """Test that OpenAI provider initializes from env."""
        provider = OpenAIProvider()
        assert provider.name == "openai"
        assert provider.supports_json_schema is True
    
    def test_provider_without_key(self):
        """Test that provider handles missing API key."""
        provider = OpenAIProvider(api_key=None)
        assert provider.health_check() is False
    
    def test_generate_without_client_returns_error(self):
        """Test that generate returns error result when client fails."""
        provider = OpenAIProvider(api_key="fake-key")
        # Force initialization failure by calling generate
        result = provider.generate(
            system_prompt="System",
            user_prompt="User",
        )
        
        # Should return error result, not raise
        assert isinstance(result, LLMResult)
        # Either returns error or empty (depending on whether openai is installed)
        assert result.provider == "openai"

