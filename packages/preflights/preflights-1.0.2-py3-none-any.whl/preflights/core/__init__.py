"""Preflights Core - Pure logic, stateless, deterministic."""

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

__all__ = [
    "process",
    "Intention",
    "Question",
    "ConversationState",
    "FileContext",
    "DecisionPatch",
    "ArchitectureState",
    "HeuristicsConfig",
    "SnapshotSchema",
    "ADR",
    "Task",
    "NeedsClarification",
    "ReadyToBuild",
    "Completed",
    "CoreError",
    "ProcessResult",
]
