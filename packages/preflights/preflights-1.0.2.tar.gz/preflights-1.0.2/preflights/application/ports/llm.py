"""LLM adapter port."""

from __future__ import annotations

from typing import Protocol

from preflights.application.types import Question
from preflights.core.types import DecisionPatch, HeuristicsConfig


class LLMPort(Protocol):
    """
    Port for LLM interactions.

    Responsible for:
    - Generating clarification questions from intention
    - Extracting structured DecisionPatch from answers

    V1: Mock adapter with deterministic behavior.
    Future: Anthropic Claude adapter.
    """

    def generate_questions(
        self,
        intention: str,
        heuristics_config: HeuristicsConfig,
        context: str | None = None,
    ) -> tuple[Question, ...]:
        """
        Generate clarification questions based on intention.

        Args:
            intention: User's intention text
            heuristics_config: Schema and heuristics configuration
            context: Optional additional context

        Returns:
            Tuple of questions to ask
        """
        ...

    def extract_decision_patch(
        self,
        intention: str,
        answers: dict[str, str | tuple[str, ...]],
        heuristics_config: HeuristicsConfig,
    ) -> DecisionPatch | None:
        """
        Extract structured DecisionPatch from answers.

        Args:
            intention: User's intention text
            answers: Question ID -> answer mapping
            heuristics_config: Schema for validation

        Returns:
            DecisionPatch if extraction successful, None if failed

        Note: Returns None if LLM cannot extract valid patch.
              Application should return PATCH_EXTRACTION_FAILED error.
        """
        ...
