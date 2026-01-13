"""
Preflights Application Layer.

Public API (FROZEN for V1):
- start_preflight(intention, repo_path) -> PreflightStartResult
- continue_preflight(session_id, answers_delta) -> PreflightContinueResult

See PREFLIGHTS_APP_CONTRACT.md for full specification.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from preflights.application.preflights_app import PreflightsApp
from preflights.application.types import (
    PreflightArtifacts,
    PreflightContinueResult,
    PreflightError,
    PreflightStartResult,
    Question,
)

if TYPE_CHECKING:
    from pathlib import Path

    from preflights.adapters.default_config import DefaultConfigLoader
    from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
    from preflights.adapters.fixed_clock import FixedClockProvider
    from preflights.adapters.in_memory_session import InMemorySessionAdapter
    from preflights.adapters.mock_llm import MockLLMAdapter
    from preflights.adapters.sequential_uid import SequentialUIDProvider
    from preflights.adapters.simple_file_context import SimpleFileContextBuilder

# Module-level default app (lazy initialized)
_default_app: PreflightsApp | None = None


def _get_default_app() -> PreflightsApp:
    """Get or create default app instance."""
    # Import adapters lazily to avoid circular imports
    from preflights.adapters.default_config import DefaultConfigLoader
    from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
    from preflights.adapters.fixed_clock import FixedClockProvider
    from preflights.adapters.in_memory_session import InMemorySessionAdapter
    from preflights.adapters.mock_llm import MockLLMAdapter
    from preflights.adapters.sequential_uid import SequentialUIDProvider
    from preflights.adapters.simple_file_context import SimpleFileContextBuilder

    global _default_app
    if _default_app is None:
        _default_app = PreflightsApp(
            session_adapter=InMemorySessionAdapter(),
            llm_adapter=MockLLMAdapter(),
            filesystem_adapter=FakeFilesystemAdapter(),
            uid_provider=SequentialUIDProvider(),
            clock_provider=FixedClockProvider(),
            file_context_builder=SimpleFileContextBuilder(),
            config_loader=DefaultConfigLoader(),
        )
    return _default_app


def start_preflight(
    intention: str,
    repo_path: str,
) -> PreflightStartResult:
    """
    Start a new clarification session.

    Args:
        intention: User's intention (e.g., "Add authentication")
        repo_path: Absolute path to repository root

    Returns:
        PreflightStartResult with session_id + initial questions

    Example:
        result = start_preflight(
            intention="Add OAuth authentication",
            repo_path="/home/user/my-project"
        )

        print(f"Session: {result.session_id}")
        for q in result.questions:
            print(f"  {q.question}")
    """
    app = _get_default_app()
    return app.start_preflight(intention, repo_path)


def continue_preflight(
    session_id: str,
    answers_delta: dict[str, str | list[str]],
) -> PreflightContinueResult:
    """
    Continue clarification with new answers.

    Args:
        session_id: Session ID from start_preflight()
        answers_delta: New answers to provide
            Format: {
                "question_id": "single_answer",  # For single_choice / free_text
                "question_id": ["answer1", "answer2"]  # For multi_choice
            }

    Returns:
        PreflightContinueResult with one of:
        - status="needs_more_answers" + remaining questions
        - status="needs_clarification" + follow-up questions
        - status="completed" + artifact paths
        - status="error" + error details

    Example:
        result = continue_preflight(
            session_id="abc-123",
            answers_delta={"auth_strategy": "OAuth"}
        )

        if result.status == "completed":
            print(f"Task: {result.artifacts.task_path}")
    """
    app = _get_default_app()
    return app.continue_preflight(session_id, answers_delta)


def create_app(
    *,
    session_adapter: "InMemorySessionAdapter | None" = None,
    llm_adapter: "MockLLMAdapter | None" = None,
    filesystem_adapter: "FakeFilesystemAdapter | None" = None,
    uid_provider: "SequentialUIDProvider | None" = None,
    clock_provider: "FixedClockProvider | None" = None,
    file_context_builder: "SimpleFileContextBuilder | None" = None,
    config_loader: "DefaultConfigLoader | None" = None,
    base_path: "Path | None" = None,
) -> PreflightsApp:
    """
    Create a PreflightsApp instance with custom adapters.

    Useful for testing with specific configurations.

    Args:
        session_adapter: Custom session storage
        llm_adapter: Custom LLM adapter
        filesystem_adapter: Custom filesystem adapter
        uid_provider: Custom UID provider
        clock_provider: Custom clock provider
        file_context_builder: Custom file context builder
        config_loader: Custom config loader
        base_path: If provided, create FakeFilesystemAdapter with this base path

    Returns:
        Configured PreflightsApp instance
    """
    # Import adapters lazily to avoid circular imports
    from preflights.adapters.default_config import DefaultConfigLoader
    from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
    from preflights.adapters.fixed_clock import FixedClockProvider
    from preflights.adapters.in_memory_session import InMemorySessionAdapter
    from preflights.adapters.mock_llm import MockLLMAdapter
    from preflights.adapters.sequential_uid import SequentialUIDProvider
    from preflights.adapters.simple_file_context import SimpleFileContextBuilder

    fs_adapter = filesystem_adapter
    if fs_adapter is None and base_path is not None:
        fs_adapter = FakeFilesystemAdapter(base_path)
    elif fs_adapter is None:
        fs_adapter = FakeFilesystemAdapter()

    return PreflightsApp(
        session_adapter=session_adapter or InMemorySessionAdapter(),
        llm_adapter=llm_adapter or MockLLMAdapter(),
        filesystem_adapter=fs_adapter,
        uid_provider=uid_provider or SequentialUIDProvider(),
        clock_provider=clock_provider or FixedClockProvider(),
        file_context_builder=file_context_builder or SimpleFileContextBuilder(),
        config_loader=config_loader or DefaultConfigLoader(),
    )


# Public exports (strict __all__ as per contract)
__all__ = [
    "start_preflight",
    "continue_preflight",
    # Types needed by clients
    "PreflightStartResult",
    "PreflightContinueResult",
    "PreflightArtifacts",
    "PreflightError",
    "Question",
    # Factory for testing
    "create_app",
    "PreflightsApp",
]
