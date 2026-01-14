"""
Base LLM Adapter.

Abstract base class for LLM adapters with retry and timeout logic.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from preflights.adapters.llm_errors import (
    LLMInvalidResponseError,
    LLMProviderError,
    LLMTimeoutError,
)
from preflights.adapters.llm_prompts import (
    CLARIFICATION_SYSTEM_PROMPT,
    CLARIFICATION_TOOL_SCHEMA,
    DECISION_TOOL_SCHEMA,
    EXTRACTION_SYSTEM_PROMPT,
)
from preflights.adapters.llm_validation import (
    validate_and_repair_clarification,
    validate_and_repair_decision,
)
from preflights.application.llm_config import DEFAULT_MODELS, LLMConfig
from preflights.application.types import (
    LLMContext,
    LLMResponse,
    Question,
    SessionSnapshot,
)
from preflights.core.types import DecisionPatch, HeuristicsConfig

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class BaseLLMAdapter(ABC):
    """Base class for LLM adapters with retry and timeout logic."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize adapter with configuration."""
        self._config = config
        self._model = config.model or DEFAULT_MODELS.get(config.provider, "")

    @property
    def provider(self) -> str:
        """Get provider name."""
        return self._config.provider

    @abstractmethod
    def _call_api(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Make raw API call to the LLM provider.

        Args:
            system_prompt: System prompt
            user_message: User message
            tools: Tool/function schemas

        Returns:
            Parsed tool/function call result

        Raises:
            LLMTimeoutError: On timeout
            LLMProviderError: On API error
            LLMInvalidResponseError: On invalid response
        """
        ...

    def generate_questions(
        self,
        intention: str,
        heuristics_config: HeuristicsConfig,
        context: LLMContext | None = None,
        session_state: SessionSnapshot | None = None,
    ) -> LLMResponse:
        """
        Generate clarification questions with retry logic.

        Args:
            intention: User's intention text
            heuristics_config: Schema and heuristics configuration
            context: Optional filtered context
            session_state: Optional session snapshot for cross-session tracking

        Returns:
            LLMResponse with questions and semantic tracking
        """
        user_message = self._build_question_prompt(
            intention, heuristics_config, context, session_state
        )

        for attempt in range(self._config.max_retries + 1):
            try:
                result = self._call_api(
                    system_prompt=CLARIFICATION_SYSTEM_PROMPT,
                    user_message=user_message,
                    tools=[CLARIFICATION_TOOL_SCHEMA],
                )
                return self._parse_question_response(result)
            except LLMTimeoutError:
                logger.warning(f"LLM timeout on attempt {attempt + 1}")
                if attempt == self._config.max_retries:
                    raise
            except LLMInvalidResponseError as e:
                logger.warning(f"Invalid LLM response on attempt {attempt + 1}: {e}")
                if attempt == self._config.max_retries:
                    raise

        raise LLMProviderError("Max retries exceeded")

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
        """
        user_message = self._build_extraction_prompt(
            intention, answers, heuristics_config
        )

        for attempt in range(self._config.max_retries + 1):
            try:
                result = self._call_api(
                    system_prompt=EXTRACTION_SYSTEM_PROMPT,
                    user_message=user_message,
                    tools=[DECISION_TOOL_SCHEMA],
                )
                return self._parse_decision_response(result, heuristics_config)
            except LLMTimeoutError:
                logger.warning(f"LLM timeout on extraction attempt {attempt + 1}")
                if attempt == self._config.max_retries:
                    return None
            except LLMInvalidResponseError as e:
                logger.warning(f"Invalid extraction response on attempt {attempt + 1}: {e}")
                if attempt == self._config.max_retries:
                    return None

        return None

    def _build_question_prompt(
        self,
        intention: str,
        heuristics_config: HeuristicsConfig,
        context: LLMContext | None,
        session_state: SessionSnapshot | None,
    ) -> str:
        """Build user message for question generation."""
        parts = [f"User intention: {intention}"]

        # Add schema information
        categories = [cat for cat, _ in heuristics_config.schema.categories]
        parts.append(f"\nAvailable categories: {', '.join(categories)}")

        # Add context if provided
        if context:
            parts.append(f"\nRepository summary:\n{context.file_summary}")
            if context.architecture_summary:
                parts.append(f"\nExisting architecture:\n{context.architecture_summary}")

        # Add session state if provided
        if session_state:
            if session_state.asked_questions:
                parts.append(
                    f"\nAlready asked questions: {', '.join(session_state.asked_questions)}"
                )
            if session_state.missing_info:
                parts.append(
                    f"\nStill missing information: {', '.join(session_state.missing_info)}"
                )

        parts.append("\nGenerate clarification questions to understand this intention better.")

        return "\n".join(parts)

    def _build_extraction_prompt(
        self,
        intention: str,
        answers: dict[str, str | tuple[str, ...]],
        heuristics_config: HeuristicsConfig,
    ) -> str:
        """Build user message for decision extraction."""
        parts = [f"User intention: {intention}"]

        # Add answers
        parts.append("\nClarification answers:")
        for q_id, answer in answers.items():
            if isinstance(answer, tuple):
                answer_str = ", ".join(answer)
            else:
                answer_str = answer
            parts.append(f"  - {q_id}: {answer_str}")

        # Add schema information
        categories = [cat for cat, _ in heuristics_config.schema.categories]
        parts.append(f"\nAvailable categories: {', '.join(categories)}")

        parts.append("\nExtract the architecture decision from these answers.")

        return "\n".join(parts)

    def _parse_question_response(self, result: dict[str, Any]) -> LLMResponse:
        """Parse tool call result into LLMResponse."""
        try:
            # Validate and repair response (handles max questions, progress invariants, etc.)
            validated = validate_and_repair_clarification(result)

            # If validation returned LLMResponse, use it directly
            if isinstance(validated, LLMResponse):
                return validated

            # Otherwise build from validated dict
            raw_questions = validated.get("questions", [])
            missing_info = tuple(validated.get("missing_info", []))
            decision_hint = validated.get("decision_hint", "unsure")
            progress = float(validated.get("progress", 0.5))

            # Validate decision_hint
            if decision_hint not in ("task", "adr", "unsure"):
                decision_hint = "unsure"

            # Parse questions
            questions: list[Question] = []
            for q in raw_questions:
                q_dict = q if isinstance(q, dict) else {}
                q_type = q_dict.get("type", "free_text")
                if q_type not in ("single_choice", "multi_choice", "free_text"):
                    q_type = "free_text"

                options = None
                if q_type in ("single_choice", "multi_choice"):
                    raw_options = q_dict.get("options", [])
                    if raw_options:
                        options = tuple(str(o) for o in raw_options)

                questions.append(
                    Question(
                        id=str(q_dict.get("id", f"q_{len(questions)}")),
                        type=q_type,
                        question=str(q_dict.get("question", "")),
                        options=options,
                        optional=bool(q_dict.get("optional", False)),
                    )
                )

            return LLMResponse(
                questions=tuple(questions),
                missing_info=missing_info,
                decision_hint=decision_hint,
                progress=progress,
            )
        except Exception as e:
            raise LLMInvalidResponseError(f"Failed to parse question response: {e}") from e

    def _parse_decision_response(
        self,
        result: dict[str, Any],
        heuristics_config: HeuristicsConfig,
    ) -> DecisionPatch | None:
        """Parse tool call result into DecisionPatch."""
        try:
            # Validate and repair response
            validated = validate_and_repair_decision(result)

            # Check status - return None if insufficient
            status = validated.get("status")
            if status == "insufficient":
                reason = validated.get("reason", "Unknown reason")
                logger.info(f"LLM returned insufficient: {reason}")
                return None

            category = str(validated.get("category", "Other"))
            raw_fields = validated.get("fields", [])

            # Validate category against schema
            valid_categories = [cat for cat, _ in heuristics_config.schema.categories]
            if category not in valid_categories:
                category = "Other"

            # Parse fields
            fields: list[tuple[str, str]] = []
            for f in raw_fields:
                key = str(f.get("key", ""))
                value = str(f.get("value", ""))
                if key and value:
                    fields.append((key, value))

            if not fields:
                return None

            return DecisionPatch(
                category=category,
                fields=tuple(fields),
            )
        except Exception as e:
            logger.warning(f"Failed to parse decision response: {e}")
            return None
