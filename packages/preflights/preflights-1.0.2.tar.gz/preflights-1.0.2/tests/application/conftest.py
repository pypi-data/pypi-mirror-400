"""Shared fixtures for Application tests.

Provides reusable fixtures for testing PreflightsApp.
Uses fake/mock adapters for deterministic testing.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from preflights.adapters.default_config import DefaultConfigLoader
from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
from preflights.adapters.fixed_clock import FixedClockProvider
from preflights.adapters.in_memory_session import InMemorySessionAdapter
from preflights.adapters.mock_llm import MockLLMAdapter
from preflights.adapters.sequential_uid import SequentialUIDProvider
from preflights.adapters.simple_file_context import SimpleFileContextBuilder
from preflights.application.preflights_app import PreflightsApp
from preflights.core.types import FileContext, HeuristicsConfig, default_v1_heuristics

if TYPE_CHECKING:
    pass


# =============================================================================
# ADAPTER FIXTURES
# =============================================================================


@pytest.fixture
def session_adapter() -> InMemorySessionAdapter:
    """Fresh in-memory session adapter."""
    return InMemorySessionAdapter()


@pytest.fixture
def llm_adapter() -> MockLLMAdapter:
    """Mock LLM adapter with deterministic responses."""
    return MockLLMAdapter()


@pytest.fixture
def clock() -> FixedClockProvider:
    """Fixed clock for deterministic timestamps."""
    return FixedClockProvider(
        fixed_unix=1736161200.0,  # 2025-01-06T11:00:00Z
        fixed_iso="2025-01-06T11:00:00Z",
    )


@pytest.fixture
def uid_provider() -> SequentialUIDProvider:
    """Sequential UID provider for deterministic UIDs."""
    return SequentialUIDProvider()


@pytest.fixture
def file_context_builder() -> SimpleFileContextBuilder:
    """Simple file context builder."""
    return SimpleFileContextBuilder()


@pytest.fixture
def config_loader() -> DefaultConfigLoader:
    """Default config loader."""
    return DefaultConfigLoader()


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Temporary repository directory."""
    repo = tmp_path / "test-repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    return repo


@pytest.fixture
def filesystem_adapter(tmp_repo: Path) -> FakeFilesystemAdapter:
    """Filesystem adapter for temp directory."""
    return FakeFilesystemAdapter(tmp_repo)


# =============================================================================
# APP FIXTURES
# =============================================================================


@pytest.fixture
def app(
    session_adapter: InMemorySessionAdapter,
    llm_adapter: MockLLMAdapter,
    filesystem_adapter: FakeFilesystemAdapter,
    uid_provider: SequentialUIDProvider,
    clock: FixedClockProvider,
    file_context_builder: SimpleFileContextBuilder,
    config_loader: DefaultConfigLoader,
) -> PreflightsApp:
    """Fully configured PreflightsApp with fake adapters."""
    return PreflightsApp(
        session_adapter=session_adapter,
        llm_adapter=llm_adapter,
        filesystem_adapter=filesystem_adapter,
        uid_provider=uid_provider,
        clock_provider=clock,
        file_context_builder=file_context_builder,
        config_loader=config_loader,
    )


# =============================================================================
# CONTEXT FIXTURES
# =============================================================================


@pytest.fixture
def fixed_file_context() -> FileContext:
    """Fixed file context for deterministic tests."""
    return FileContext(
        paths=("src/auth/login.ts", "src/auth/session.ts"),
        high_level_dirs=("src/",),
        signals=(("language", "typescript"),),
    )


@pytest.fixture
def heuristics() -> HeuristicsConfig:
    """Default V1 heuristics."""
    return default_v1_heuristics()


# =============================================================================
# HELPER FIXTURES
# =============================================================================


@pytest.fixture
def valid_intention() -> str:
    """Valid intention string."""
    return "Add OAuth authentication"


@pytest.fixture
def valid_repo_path(tmp_repo: Path) -> str:
    """Valid repository path as string."""
    return str(tmp_repo)
