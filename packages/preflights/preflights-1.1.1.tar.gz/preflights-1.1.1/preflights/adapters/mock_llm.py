"""Mock LLM adapter for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from preflights.application.types import LLMContext, LLMResponse, Question, SessionSnapshot
from preflights.core.types import DecisionPatch, HeuristicsConfig

if TYPE_CHECKING:
    pass

# Canonical value for "Other" option - MUST remain constant across all locales
OTHER_SPECIFY = "Other (specify)"


class MockLLMAdapter:
    """
    Deterministic mock LLM adapter.

    Returns fixed questions and patches based on keywords in intention.
    Used for testing without calling real LLM.
    Also serves as fallback when real LLM is unavailable.
    """

    def __init__(
        self,
        force_invalid_patch: bool = False,
        force_extraction_failure: bool = False,
    ) -> None:
        """
        Initialize mock LLM.

        Args:
            force_invalid_patch: If True, return invalid category in patch
            force_extraction_failure: If True, return None from extract
        """
        self._force_invalid_patch = force_invalid_patch
        self._force_extraction_failure = force_extraction_failure
        self._override_questions: tuple[Question, ...] | None = None
        self._is_fallback: bool = False  # Set by factory when used as fallback

    @property
    def is_fallback(self) -> bool:
        """Check if this adapter is being used as a fallback."""
        return self._is_fallback

    def set_questions(self, questions: list[Question]) -> None:
        """Set override questions for testing."""
        self._override_questions = tuple(questions)

    def clear_questions_override(self) -> None:
        """Clear questions override."""
        self._override_questions = None

    def _make_choice_question(
        self,
        qid: str,
        question_text: str,
        options: tuple[str, ...],
        question_type: Literal["single_choice", "multi_choice"] = "single_choice",
        optional: bool = False,
    ) -> list[Question]:
        """
        Create a choice question with 'Other (specify)' option.

        Returns a list containing:
        1. The main choice question (with OTHER_SPECIFY added to options)
        2. The associated __other free-text question (conditional, optional)
        """
        # Add "Other (specify)" to options
        options_with_other = options + (OTHER_SPECIFY,)

        main_question = Question(
            id=qid,
            type=question_type,
            question=question_text,
            options=options_with_other,
            optional=optional,
        )

        # Generate the __other question (hidden, conditional)
        other_question = Question(
            id=f"{qid}__other",
            type="free_text",
            question=f"Please specify ({question_text}):",
            optional=True,  # Only required if "Other (specify)" is selected
            depends_on_question_id=qid,
            depends_on_value=OTHER_SPECIFY,
        )

        return [main_question, other_question]

    def _resolve_other_value(
        self,
        answers: dict[str, str | tuple[str, ...]],
        qid: str,
        default: str,
    ) -> str:
        """Resolve answer value, using __other if 'Other (specify)' was selected."""
        value = answers.get(qid, default)
        if isinstance(value, tuple):
            value = value[0] if value else default

        # If "Other (specify)" was selected, use the __other value
        if value == OTHER_SPECIFY:
            other_value = answers.get(f"{qid}__other", default)
            if isinstance(other_value, tuple):
                other_value = other_value[0] if other_value else default
            return str(other_value) if other_value else default

        return str(value)

    def generate_questions(
        self,
        intention: str,
        heuristics_config: HeuristicsConfig,
        context: LLMContext | None = None,
        session_state: SessionSnapshot | None = None,
    ) -> LLMResponse:
        """Generate deterministic questions based on keywords.

        Returns LLMResponse with questions and semantic tracking fields.
        """
        # Use override if set
        if self._override_questions is not None:
            override_questions = self._override_questions
            return LLMResponse(
                questions=override_questions,
                missing_info=tuple(q.id for q in override_questions if not q.depends_on_question_id),
                decision_hint="unsure",
                progress=0.5,
            )

        intention_lower = intention.lower()
        questions: list[Question] = []
        decision_hint: Literal["task", "adr", "unsure"] = "unsure"

        # Auth-related questions
        if any(kw in intention_lower for kw in ["auth", "login", "oauth"]):
            questions.extend(
                self._make_choice_question(
                    "auth_strategy",
                    "Which authentication strategy do you want to use?",
                    ("OAuth", "Email/Password", "Magic Link"),
                )
            )
            questions.extend(
                self._make_choice_question(
                    "auth_library",
                    "Which authentication library do you prefer?",
                    ("next-auth", "passport", "custom"),
                )
            )
            decision_hint = "adr"  # Auth is typically architectural

        # Database-related questions
        elif any(kw in intention_lower for kw in ["database", "db", "postgres", "sql"]):
            questions.extend(
                self._make_choice_question(
                    "db_type",
                    "Which database type do you want to use?",
                    ("PostgreSQL", "MySQL", "MongoDB"),
                )
            )
            questions.extend(
                self._make_choice_question(
                    "db_orm",
                    "Which ORM do you want to use?",
                    ("Prisma", "TypeORM", "Drizzle"),
                )
            )
            decision_hint = "adr"  # Database is typically architectural

        # Frontend-related questions
        elif any(kw in intention_lower for kw in ["frontend", "ui", "react", "component"]):
            questions.extend(
                self._make_choice_question(
                    "frontend_framework",
                    "Which frontend framework?",
                    ("React", "Vue", "Svelte"),
                )
            )
            questions.extend(
                self._make_choice_question(
                    "styling",
                    "Which styling approach?",
                    ("Tailwind", "CSS Modules", "Styled Components"),
                )
            )
            decision_hint = "task"  # Frontend changes are often tasks

        # Default: generic questions
        else:
            questions.extend(
                self._make_choice_question(
                    "category",
                    "Which category does this change belong to?",
                    ("Frontend", "Backend", "Database", "Authentication", "Infra"),
                )
            )
            questions.append(
                Question(
                    id="description",
                    type="free_text",
                    question="Please describe the technical approach:",
                    optional=False,
                )
            )
            decision_hint = "unsure"

        # Build missing_info from non-conditional questions
        missing_info = tuple(
            q.id for q in questions if not q.depends_on_question_id
        )

        return LLMResponse(
            questions=tuple(questions),
            missing_info=missing_info,
            decision_hint=decision_hint,
            progress=0.5,  # Mock always returns 50% progress
        )

    def extract_decision_patch(
        self,
        intention: str,
        answers: dict[str, str | tuple[str, ...]],
        heuristics_config: HeuristicsConfig,
    ) -> DecisionPatch | None:
        """Extract DecisionPatch from answers."""
        if self._force_extraction_failure:
            return None

        intention_lower = intention.lower()

        # Invalid patch for testing error handling
        if self._force_invalid_patch:
            return DecisionPatch(
                category="InvalidCategory",
                fields=(("Field", "Value"),),
            )

        # Auth-related patch
        if any(kw in intention_lower for kw in ["auth", "login", "oauth"]):
            strategy = self._resolve_other_value(answers, "auth_strategy", "OAuth")
            library = self._resolve_other_value(answers, "auth_library", "next-auth")

            return DecisionPatch(
                category="Authentication",
                fields=(
                    ("Strategy", strategy),
                    ("Library", library),
                ),
            )

        # Database-related patch
        if any(kw in intention_lower for kw in ["database", "db", "postgres", "sql"]):
            db_type = self._resolve_other_value(answers, "db_type", "PostgreSQL")
            orm = self._resolve_other_value(answers, "db_orm", "Prisma")

            return DecisionPatch(
                category="Database",
                fields=(
                    ("Type", db_type),
                    ("ORM", orm),
                ),
            )

        # Frontend-related patch
        if any(kw in intention_lower for kw in ["frontend", "ui", "react", "component"]):
            framework = self._resolve_other_value(answers, "frontend_framework", "React")
            styling = self._resolve_other_value(answers, "styling", "Tailwind")

            return DecisionPatch(
                category="Frontend",
                fields=(
                    ("Framework", framework),
                    ("Styling", styling),
                ),
            )

        # Default: use resolved category with dynamic fields
        category = self._resolve_other_value(answers, "category", "Other")

        description = answers.get("description", "Implementation")
        if isinstance(description, tuple):
            description = description[0] if description else "Implementation"

        return DecisionPatch(
            category=str(category),
            fields=(("Description", str(description)),),
        )
