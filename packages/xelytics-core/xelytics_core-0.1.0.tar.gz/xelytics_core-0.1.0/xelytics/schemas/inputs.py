"""Input schemas for analysis.

Defines the input contract for the analyze() function.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd


@dataclass
class DatasetInput:
    """Input dataset with optional metadata.
    
    Primary input is a pandas DataFrame.
    Optional metadata can provide hints for analysis.
    """
    data: pd.DataFrame
    
    # Optional metadata
    name: Optional[str] = None
    description: Optional[str] = None
    
    # Column hints (optional - analysis should work without these)
    column_descriptions: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate input data."""
        if not isinstance(self.data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        if self.data.empty:
            raise ValueError("data cannot be empty")
    
    @property
    def row_count(self) -> int:
        """Number of rows in the dataset."""
        return len(self.data)
    
    @property
    def column_count(self) -> int:
        """Number of columns in the dataset."""
        return len(self.data.columns)
    
    @property
    def columns(self) -> List[str]:
        """List of column names."""
        return list(self.data.columns)
