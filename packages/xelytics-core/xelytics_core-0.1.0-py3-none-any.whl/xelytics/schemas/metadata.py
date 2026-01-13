"""Metadata schemas for run tracking.

Captures decision logs and execution metadata.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class DecisionType(str, Enum):
    """Types of decisions made during analysis."""
    TEST_SELECTED = "test_selected"
    TEST_SKIPPED = "test_skipped"
    FALLBACK_USED = "fallback_used"
    ASSUMPTION_CHECKED = "assumption_checked"
    VISUALIZATION_GENERATED = "visualization_generated"
    INSIGHT_GENERATED = "insight_generated"


@dataclass
class DecisionLogEntry:
    """A single decision made during analysis.
    
    NO AUTO MAGIC: Every decision must be logged with reason.
    """
    decision_type: DecisionType
    description: str
    reason: str
    
    # What was affected
    affected_columns: List[str] = field(default_factory=list)
    
    # Related entities
    test_name: Optional[str] = None
    original_test: Optional[str] = None  # For fallbacks
    
    # Additional context
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "decision_type": self.decision_type.value,
            "description": self.description,
            "reason": self.reason,
            "affected_columns": self.affected_columns,
            "test_name": self.test_name,
            "original_test": self.original_test,
            "context": self.context,
        }


@dataclass
class DecisionLog:
    """Machine-readable decision log.
    
    Every statistical decision must be explainable without reading code.
    """
    entries: List[DecisionLogEntry] = field(default_factory=list)
    
    def add_test_selected(
        self,
        test_name: str,
        columns: List[str],
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a test selection decision."""
        self.entries.append(DecisionLogEntry(
            decision_type=DecisionType.TEST_SELECTED,
            description=f"Selected {test_name} for columns {columns}",
            reason=reason,
            affected_columns=columns,
            test_name=test_name,
            context=context or {},
        ))
    
    def add_test_skipped(
        self,
        test_name: str,
        columns: List[str],
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a test skip decision."""
        self.entries.append(DecisionLogEntry(
            decision_type=DecisionType.TEST_SKIPPED,
            description=f"Skipped {test_name} for columns {columns}",
            reason=reason,
            affected_columns=columns,
            test_name=test_name,
            context=context or {},
        ))
    
    def add_fallback(
        self,
        original_test: str,
        fallback_test: str,
        columns: List[str],
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a fallback decision."""
        self.entries.append(DecisionLogEntry(
            decision_type=DecisionType.FALLBACK_USED,
            description=f"Fallback from {original_test} to {fallback_test}",
            reason=reason,
            affected_columns=columns,
            test_name=fallback_test,
            original_test=original_test,
            context=context or {},
        ))
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convert all entries to list of dictionaries."""
        return [e.to_dict() for e in self.entries]
    
    def get_by_type(self, decision_type: DecisionType) -> List[DecisionLogEntry]:
        """Get all entries of a specific type."""
        return [e for e in self.entries if e.decision_type == decision_type]
