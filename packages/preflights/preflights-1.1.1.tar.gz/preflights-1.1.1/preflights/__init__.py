"""Preflights - Architecture Decision Automation Platform."""

from preflights.core.process import process
from preflights.core.types import (
    ADR,
    ArchitectureState,
    Completed,
    ConversationState,
    CoreError,
    DecisionPatch,
    FileContext,
    HeuristicsConfig,
    Intention,
    NeedsClarification,
    ProcessResult,
    Question,
    ReadyToBuild,
    SnapshotSchema,
    Task,
)

__version__ = "0.1.0"

__all__ = [
    # Main entry point
    "process",
    # Input types
    "Intention",
    "Question",
    "ConversationState",
    "FileContext",
    "DecisionPatch",
    "ArchitectureState",
    "HeuristicsConfig",
    "SnapshotSchema",
    # Output types
    "ADR",
    "Task",
    # Result types
    "NeedsClarification",
    "ReadyToBuild",
    "Completed",
    "CoreError",
    "ProcessResult",
]
