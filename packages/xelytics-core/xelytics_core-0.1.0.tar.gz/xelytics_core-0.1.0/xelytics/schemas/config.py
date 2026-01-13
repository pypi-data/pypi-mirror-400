"""Analysis configuration schema.

Typed models only. No dicts crossing boundaries. Defaults explicit.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional, List


@dataclass
class AnalysisConfig:
    """Configuration for analysis execution.
    
    All parameters have explicit defaults.
    This contract is frozen - changes require version bump.
    """
    
    # Analysis mode
    mode: Literal["automated", "semi-automated"] = "automated"
    
    # Statistical settings
    significance_level: float = 0.05
    
    # LLM settings
    enable_llm_insights: bool = True
    llm_provider: Literal["grok", "openai"] = "openai"
    
    # Output limits
    max_visualizations: int = 10
    max_insights: int = 20
    
    # Feature toggles
    include_assumptions: bool = True
    include_effect_sizes: bool = True
    include_confidence_intervals: bool = True
    
    # Column filtering (optional)
    include_columns: Optional[List[str]] = None
    exclude_columns: Optional[List[str]] = None
    
    # Target column for supervised analysis (optional)
    target_column: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration values."""
        if not 0 < self.significance_level < 1:
            raise ValueError("significance_level must be between 0 and 1")
        if self.max_visualizations < 0:
            raise ValueError("max_visualizations must be non-negative")
        if self.max_insights < 0:
            raise ValueError("max_insights must be non-negative")
