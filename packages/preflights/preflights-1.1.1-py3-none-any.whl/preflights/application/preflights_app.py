"""
PreflightsApp - Application Orchestrator.

Implements the public contract (PREFLIGHTS_APP_CONTRACT.md):
- start_preflight()
- continue_preflight()

This module coordinates Core, Adapters, and manages the multi-turn flow.
"""

from __future__ import annotations

from preflights.adapters.in_memory_session import InMemorySessionAdapter
from preflights.application.ports.clock import ClockPort
from preflights.application.ports.config import ConfigLoaderPort
from preflights.application.ports.file_context import FileContextBuilderPort
from preflights.application.ports.filesystem import FilesystemPort, ParseError
from preflights.application.ports.llm import LLMPort
from preflights.application.ports.session import SessionPort
from preflights.application.ports.uid import UIDProviderPort
from preflights.application.prompt_builder import AGENT_PROMPT_PATH, build_agent_prompt
from preflights.application.types import (
    AppErrorCode,
    PreflightArtifacts,
    PreflightContinueResult,
    PreflightError,
    PreflightStartResult,
    Question,
    Session,
)
from preflights.core.process import process as core_process
from preflights.core.types import (
    Answer,
    ArchitectureState,
    Completed,
    ConversationState,
    CoreError,
    DecisionPatch,
    FileContext,
    HeuristicsConfig,
    Intention,
    NeedsClarification,
    ReadyToBuild,
)
from preflights.core.types import Question as CoreQuestion


class PreflightsApp:
    """
    Application orchestrator for Preflights.

    Coordinates:
    - Session management
    - LLM interactions (question generation, patch extraction)
    - Core logic (validation, artifact building)
    - Filesystem operations (writing artifacts)

    Public API:
    - start_preflight(intention, repo_path) -> PreflightStartResult
    - continue_preflight(session_id, answers_delta) -> PreflightContinueResult
    """

    SESSION_TTL_SECONDS: float = 30 * 60  # 30 minutes

    def __init__(
        self,
        session_adapter: SessionPort,
        llm_adapter: LLMPort,
        filesystem_adapter: FilesystemPort,
        uid_provider: UIDProviderPort,
        clock_provider: ClockPort,
        file_context_builder: FileContextBuilderPort,
        config_loader: ConfigLoaderPort,
    ) -> None:
        """
        Initialize PreflightsApp with adapters.

        All adapters are injected (dependency inversion).
        """
        self._session = session_adapter
        self._llm = llm_adapter
        self._fs = filesystem_adapter
        self._uid = uid_provider
        self._clock = clock_provider
        self._file_context = file_context_builder
        self._config = config_loader

    def start_preflight(
        self,
        intention: str,
        repo_path: str,
    ) -> PreflightStartResult:
        """
        Start a new clarification session.

        Steps:
        1. Validate repo exists
        2. Load configuration
        3. Build file context
        4. Generate questions via LLM
        5. Create session
        6. Return session_id + questions
        """
        # 1. Validate repo exists
        if not self._fs.repo_exists(repo_path):
            raise PreflightAppError(
                code=AppErrorCode.REPO_NOT_FOUND,
                message=f"Repository not found: {repo_path}",
                recovery_hint="Check the path exists and is accessible",
            )

        # 2. Load configuration
        heuristics_config = self._config.load(repo_path)

        # 3. Build file context
        file_context = self._file_context.build(repo_path)

        # 4. Generate questions via LLM
        llm_response = self._llm.generate_questions(
            intention=intention,
            heuristics_config=heuristics_config,
            context=None,
            session_state=None,
        )

        # 5. Create session with LLM tracking
        now = self._clock.now_unix()
        session_id = self._uid.generate_session_id()

        # Check if this is a fallback (MockLLMAdapter with _is_fallback flag)
        llm_fallback_occurred = getattr(self._llm, "_is_fallback", False)
        llm_provider_used = getattr(self._llm, "provider", "mock")

        session = Session(
            id=session_id,
            repo_path=repo_path,
            intention=intention,
            created_at=now,
            expires_at=now + self.SESSION_TTL_SECONDS,
            asked_questions=llm_response.questions,
            answers={},
            core_questions_asked=(),
            all_answers={},
            # LLM tracking fields
            missing_info=llm_response.missing_info,
            decision_hint=llm_response.decision_hint,
            llm_provider_used=llm_provider_used,
            llm_fallback_occurred=llm_fallback_occurred,
        )
        self._session.create(session)

        # 6. Return result
        return PreflightStartResult(
            session_id=session_id,
            questions=llm_response.questions,
        )

    def continue_preflight(
        self,
        session_id: str,
        answers_delta: dict[str, str | list[str]],
    ) -> PreflightContinueResult:
        """
        Continue clarification with new answers.

        Steps:
        1. Load and validate session
        2. Merge answers_delta
        3. Check if all required questions answered (Application responsibility)
        4. If incomplete → needs_more_answers
        5. Extract decision patch via LLM
        6. Call Core (pass 1 - without UIDs)
        7. Handle Core result:
           - NeedsClarification → save questions, return needs_clarification
           - CoreError → return error
           - ReadyToBuild → generate UIDs, call Core (pass 2)
        8. If Completed → write artifacts, close session
        """
        # 1. Load and validate session
        session = self._session.get(session_id)
        if session is None:
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=AppErrorCode.SESSION_NOT_FOUND,
                    message=f"Session not found: {session_id}",
                    recovery_hint="Start a new session with start_preflight()",
                ),
            )

        # Check expiry
        now = self._clock.now_unix()
        if session.is_expired(now):
            self._session.delete(session_id)
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=AppErrorCode.SESSION_EXPIRED,
                    message=f"Session {session_id} expired after 30 minutes",
                    recovery_hint="Start a new session with start_preflight()",
                ),
            )

        # 2. Merge answers_delta
        for question_id, answer in answers_delta.items():
            if isinstance(answer, list):
                session.answers[question_id] = tuple(answer)
                session.all_answers[question_id] = tuple(answer)
            else:
                session.answers[question_id] = answer
                session.all_answers[question_id] = answer

        # 3. Check if all required questions answered (Application responsibility)
        unanswered_required = self._get_unanswered_required_questions(session)

        # 4. If incomplete → needs_more_answers
        if unanswered_required:
            self._session.update(session)
            return PreflightContinueResult(
                status="needs_more_answers",
                questions=unanswered_required,
            )

        # 5. Extract decision patch via LLM
        heuristics_config = self._config.load(session.repo_path)

        patch = self._llm.extract_decision_patch(
            intention=session.intention,
            answers=session.all_answers,
            heuristics_config=heuristics_config,
        )

        if patch is None:
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=AppErrorCode.PATCH_EXTRACTION_FAILED,
                    message="Failed to extract decision patch from answers",
                    recovery_hint="Review your answers and try again",
                ),
            )

        # Store patch in session
        session.decision_patch_category = patch.category
        session.decision_patch_fields = patch.fields

        # 6. Call Core (pass 1 - without UIDs)
        file_context = self._file_context.build(session.repo_path)

        # Load existing architecture
        try:
            current_architecture = self._fs.read_architecture_state(session.repo_path)
        except ParseError as e:
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=AppErrorCode.PARSE_ERROR,
                    message=f"Architecture state file is malformed: {e}",
                    details=(("path", str(e.path)),) if e.path else (),
                    recovery_hint="Fix the file manually or restore from git",
                ),
            )

        # Build conversation state for Core
        conversation_state = self._build_conversation_state(session)

        # Call Core (pass 1)
        core_result = core_process(
            intention=Intention(text=session.intention),
            current_architecture=current_architecture,
            file_context=file_context,
            conversation_state=conversation_state,
            heuristics_config=heuristics_config,
            decision_patch=patch,
            uid_for_adr=None,
            uid_for_task=None,
            now_utc=None,
        )

        # 7. Handle Core result
        if isinstance(core_result, NeedsClarification):
            # Save new questions to session
            new_questions = self._convert_core_questions(core_result.questions)
            session.core_questions_asked = session.core_questions_asked + new_questions
            session.asked_questions = session.asked_questions + new_questions
            self._session.update(session)

            return PreflightContinueResult(
                status="needs_clarification",
                questions=new_questions,
            )

        if isinstance(core_result, CoreError):
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=core_result.code,
                    message=core_result.message,
                    details=core_result.details,
                    recovery_hint=core_result.recovery_hint,
                ),
            )

        if isinstance(core_result, ReadyToBuild):
            # Generate UIDs and call Core (pass 2)
            return self._complete_preflight(
                session=session,
                patch=patch,
                file_context=file_context,
                current_architecture=current_architecture,
                heuristics_config=heuristics_config,
                ready_to_build=core_result,
            )

        # Should not reach here
        return PreflightContinueResult(
            status="error",
            error=PreflightError(
                code=AppErrorCode.VALIDATION_FAILED,
                message=f"Unexpected Core result type: {type(core_result)}",
            ),
        )

    def _complete_preflight(
        self,
        session: Session,
        patch: DecisionPatch,
        file_context: FileContext,
        current_architecture: ArchitectureState | None,
        heuristics_config: HeuristicsConfig,
        ready_to_build: ReadyToBuild,
    ) -> PreflightContinueResult:
        """Complete preflight: generate UIDs, call Core pass 2, write artifacts."""
        # Generate UIDs (order matters: ADR first if needed, then Task)
        uid_for_adr: str | None = None
        if ready_to_build.needs_adr:
            uid_for_adr = self._uid.generate()

        uid_for_task = self._uid.generate()
        now_utc = self._clock.now_utc_iso()

        # Build conversation state
        conversation_state = self._build_conversation_state(session)

        # Call Core (pass 2 - with UIDs)
        core_result = core_process(
            intention=Intention(text=session.intention),
            current_architecture=current_architecture,
            file_context=file_context,
            conversation_state=conversation_state,
            heuristics_config=heuristics_config,
            decision_patch=patch,
            uid_for_adr=uid_for_adr,
            uid_for_task=uid_for_task,
            now_utc=now_utc,
        )

        # Handle result
        if isinstance(core_result, CoreError):
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=core_result.code,
                    message=core_result.message,
                    details=core_result.details,
                    recovery_hint=core_result.recovery_hint,
                ),
            )

        if not isinstance(core_result, Completed):
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=AppErrorCode.VALIDATION_FAILED,
                    message=f"Expected Completed, got {type(core_result)}",
                ),
            )

        # Write artifacts
        try:
            artifacts = self._write_artifacts(session.repo_path, core_result)
        except ParseError as e:
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=AppErrorCode.PARSE_ERROR,
                    message=f"Failed to write artifacts: {e}",
                    details=(("path", str(e.path)),) if e.path else (),
                    recovery_hint="Fix the malformed file manually or restore from git",
                ),
            )
        except Exception as e:
            return PreflightContinueResult(
                status="error",
                error=PreflightError(
                    code=AppErrorCode.FILESYSTEM_ERROR,
                    message=f"Failed to write artifacts: {e}",
                ),
            )

        # Close session
        self._session.delete(session.id)

        return PreflightContinueResult(
            status="completed",
            artifacts=artifacts,
        )

    def _write_artifacts(
        self, repo_path: str, completed: Completed
    ) -> PreflightArtifacts:
        """Write artifacts to filesystem."""
        # Write Task (archives existing first)
        task_path = self._fs.write_task(repo_path, completed.task)

        # Write ADR if present
        adr_path: str | None = None
        if completed.adr is not None:
            adr_path = self._fs.write_adr(repo_path, completed.adr)

        # Write architecture state if updated
        architecture_state_path: str | None = None
        if completed.updated_architecture is not None:
            architecture_state_path = self._fs.write_architecture_state(
                repo_path, completed.updated_architecture
            )

        # Build and write agent prompt
        agent_prompt = build_agent_prompt(
            task_path=task_path,
            adr_path=adr_path,
            architecture_state_path=architecture_state_path,
        )
        agent_prompt_path = self._fs.write_agent_prompt(repo_path, agent_prompt)

        return PreflightArtifacts(
            task_path=task_path,
            adr_path=adr_path,
            architecture_state_path=architecture_state_path,
            agent_prompt_path=agent_prompt_path,
            agent_prompt=agent_prompt,
        )

    def _get_unanswered_required_questions(
        self, session: Session
    ) -> tuple[Question, ...]:
        """Get unanswered required questions.

        Handles conditional __other fields:
        - If depends_on_question_id is set and parent answer matches depends_on_value,
          the __other field becomes required.
        - If parent answer doesn't match, skip the __other field entirely.
        """
        unanswered: list[Question] = []
        for question in session.asked_questions:
            # Check if this is a conditional __other question
            if question.depends_on_question_id is not None:
                parent_answer = session.answers.get(question.depends_on_question_id)
                if isinstance(parent_answer, tuple):
                    parent_answer_matches = question.depends_on_value in parent_answer
                else:
                    parent_answer_matches = parent_answer == question.depends_on_value

                if parent_answer_matches:
                    # Parent has "Other (specify)" selected, __other is required
                    if question.id not in session.answers:
                        unanswered.append(question)
                # If parent doesn't match, skip this question (not needed)
                continue

            # Regular question
            if question.optional:
                continue
            if question.id not in session.answers:
                unanswered.append(question)
        return tuple(unanswered)

    def _build_conversation_state(self, session: Session) -> ConversationState | None:
        """Build ConversationState for Core from session."""
        if not session.core_questions_asked and not session.all_answers:
            return None

        # Convert questions to Core format
        core_questions: list[CoreQuestion] = []
        for q in session.core_questions_asked:
            core_questions.append(
                CoreQuestion(
                    id=q.id,
                    type=q.type,
                    question=q.question,
                    options=q.options,
                    min_selections=q.min_selections,
                    max_selections=q.max_selections,
                    optional=q.optional,
                )
            )

        # Convert answers to Core format
        core_answers: list[Answer] = []
        for question_id, value in session.all_answers.items():
            core_answers.append(Answer(question_id=question_id, value=value))

        return ConversationState(
            asked_questions=tuple(core_questions),
            answers=tuple(core_answers),
        )

    def _convert_core_questions(
        self, core_questions: tuple[CoreQuestion, ...]
    ) -> tuple[Question, ...]:
        """Convert Core questions to Application questions."""
        return tuple(
            Question(
                id=q.id,
                type=q.type,
                question=q.question,
                options=q.options,
                min_selections=q.min_selections,
                max_selections=q.max_selections,
                optional=q.optional,
            )
            for q in core_questions
        )


class PreflightAppError(Exception):
    """Exception raised by PreflightsApp."""

    def __init__(
        self,
        code: str,
        message: str,
        details: tuple[tuple[str, str], ...] = (),
        recovery_hint: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
        self.recovery_hint = recovery_hint
