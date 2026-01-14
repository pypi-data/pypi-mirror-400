"""Tests for FileSessionAdapter."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from preflights.adapters.file_session import FileSessionAdapter
from preflights.application.ports.session import (
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from preflights.application.types import Question, Session


@pytest.fixture
def sessions_dir(tmp_path: Path) -> Path:
    """Create a temporary sessions directory."""
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    return sessions


@pytest.fixture
def adapter(sessions_dir: Path) -> FileSessionAdapter:
    """Create a FileSessionAdapter with temp directory."""
    return FileSessionAdapter(sessions_dir)


@pytest.fixture
def sample_session() -> Session:
    """Create a sample session for testing."""
    now = time.time()
    return Session(
        id="session-test-001",
        repo_path="/tmp/test-repo",
        intention="Add authentication",
        created_at=now,
        expires_at=now + 1800,  # 30 minutes
        asked_questions=(
            Question(
                id="auth_strategy",
                type="single_choice",
                question="Which auth strategy?",
                options=("OAuth", "JWT"),
            ),
        ),
        answers={"auth_strategy": "OAuth"},
    )


class TestFileSessionAdapterCreate:
    """Tests for create method."""

    def test_create_stores_session(
        self, adapter: FileSessionAdapter, sample_session: Session, sessions_dir: Path
    ) -> None:
        """create() stores session to file."""
        adapter.create(sample_session)

        session_file = sessions_dir / f"{sample_session.id}.json"
        assert session_file.exists()

    def test_create_session_contains_all_data(
        self, adapter: FileSessionAdapter, sample_session: Session, sessions_dir: Path
    ) -> None:
        """Created session file contains all session data."""
        adapter.create(sample_session)

        session_file = sessions_dir / f"{sample_session.id}.json"
        data = json.loads(session_file.read_text())

        assert data["id"] == sample_session.id
        assert data["repo_path"] == sample_session.repo_path
        assert data["intention"] == sample_session.intention
        assert len(data["asked_questions"]) == 1
        assert data["answers"]["auth_strategy"] == "OAuth"

    def test_create_raises_if_exists(
        self, adapter: FileSessionAdapter, sample_session: Session
    ) -> None:
        """create() raises SessionAlreadyExistsError if session exists."""
        adapter.create(sample_session)

        with pytest.raises(SessionAlreadyExistsError):
            adapter.create(sample_session)


class TestFileSessionAdapterGet:
    """Tests for get method."""

    def test_get_returns_session(
        self, adapter: FileSessionAdapter, sample_session: Session
    ) -> None:
        """get() returns the stored session."""
        adapter.create(sample_session)

        retrieved = adapter.get(sample_session.id)

        assert retrieved is not None
        assert retrieved.id == sample_session.id
        assert retrieved.intention == sample_session.intention
        assert retrieved.repo_path == sample_session.repo_path

    def test_get_returns_none_if_not_exists(
        self, adapter: FileSessionAdapter
    ) -> None:
        """get() returns None for non-existent session."""
        result = adapter.get("nonexistent-session")
        assert result is None

    def test_get_preserves_questions(
        self, adapter: FileSessionAdapter, sample_session: Session
    ) -> None:
        """get() preserves question structure."""
        adapter.create(sample_session)

        retrieved = adapter.get(sample_session.id)

        assert retrieved is not None
        assert len(retrieved.asked_questions) == 1
        q = retrieved.asked_questions[0]
        assert q.id == "auth_strategy"
        assert q.type == "single_choice"
        assert q.options == ("OAuth", "JWT")

    def test_get_preserves_answers(
        self, adapter: FileSessionAdapter, sample_session: Session
    ) -> None:
        """get() preserves answers."""
        adapter.create(sample_session)

        retrieved = adapter.get(sample_session.id)

        assert retrieved is not None
        assert retrieved.answers == {"auth_strategy": "OAuth"}

    def test_get_returns_none_for_corrupted_file(
        self, adapter: FileSessionAdapter, sessions_dir: Path
    ) -> None:
        """get() returns None for corrupted session file."""
        # Write corrupted JSON
        session_file = sessions_dir / "corrupted-session.json"
        session_file.write_text("{ invalid json }")

        result = adapter.get("corrupted-session")
        assert result is None


class TestFileSessionAdapterUpdate:
    """Tests for update method."""

    def test_update_modifies_session(
        self, adapter: FileSessionAdapter, sample_session: Session
    ) -> None:
        """update() modifies existing session."""
        adapter.create(sample_session)

        # Modify session
        updated = Session(
            id=sample_session.id,
            repo_path=sample_session.repo_path,
            intention=sample_session.intention,
            created_at=sample_session.created_at,
            expires_at=sample_session.expires_at,
            asked_questions=sample_session.asked_questions,
            answers={"auth_strategy": "JWT"},  # Changed
        )
        adapter.update(updated)

        retrieved = adapter.get(sample_session.id)
        assert retrieved is not None
        assert retrieved.answers == {"auth_strategy": "JWT"}

    def test_update_raises_if_not_exists(
        self, adapter: FileSessionAdapter, sample_session: Session
    ) -> None:
        """update() raises SessionNotFoundError if session doesn't exist."""
        with pytest.raises(SessionNotFoundError):
            adapter.update(sample_session)


class TestFileSessionAdapterDelete:
    """Tests for delete method."""

    def test_delete_removes_session(
        self, adapter: FileSessionAdapter, sample_session: Session, sessions_dir: Path
    ) -> None:
        """delete() removes session file."""
        adapter.create(sample_session)
        session_file = sessions_dir / f"{sample_session.id}.json"
        assert session_file.exists()

        adapter.delete(sample_session.id)

        assert not session_file.exists()

    def test_delete_is_idempotent(
        self, adapter: FileSessionAdapter
    ) -> None:
        """delete() doesn't raise for non-existent session."""
        # Should not raise
        adapter.delete("nonexistent-session")


class TestFileSessionAdapterCleanup:
    """Tests for cleanup_expired method."""

    def test_cleanup_removes_expired_sessions(
        self, adapter: FileSessionAdapter, sessions_dir: Path
    ) -> None:
        """cleanup_expired() removes expired sessions."""
        now = time.time()

        # Create expired session
        expired = Session(
            id="expired-session",
            repo_path="/tmp/repo",
            intention="Test",
            created_at=now - 3600,  # 1 hour ago
            expires_at=now - 1800,  # Expired 30 min ago
        )
        adapter.create(expired)

        # Create valid session
        valid = Session(
            id="valid-session",
            repo_path="/tmp/repo",
            intention="Test",
            created_at=now,
            expires_at=now + 1800,  # Expires in 30 min
        )
        adapter.create(valid)

        # Cleanup
        removed = adapter.cleanup_expired(now)

        assert removed == 1
        assert adapter.get("expired-session") is None
        assert adapter.get("valid-session") is not None

    def test_cleanup_handles_empty_directory(
        self, adapter: FileSessionAdapter
    ) -> None:
        """cleanup_expired() handles empty sessions directory."""
        removed = adapter.cleanup_expired(time.time())
        assert removed == 0

    def test_cleanup_removes_corrupted_files(
        self, adapter: FileSessionAdapter, sessions_dir: Path
    ) -> None:
        """cleanup_expired() removes corrupted session files."""
        # Write corrupted file
        corrupted = sessions_dir / "corrupted.json"
        corrupted.write_text("not json")

        removed = adapter.cleanup_expired(time.time())

        assert removed == 1
        assert not corrupted.exists()


class TestFileSessionAdapterHelpers:
    """Tests for helper methods."""

    def test_clear_removes_all_sessions(
        self, adapter: FileSessionAdapter
    ) -> None:
        """clear() removes all sessions."""
        now = time.time()
        for i in range(3):
            session = Session(
                id=f"session-{i}",
                repo_path="/tmp/repo",
                intention="Test",
                created_at=now,
                expires_at=now + 1800,
            )
            adapter.create(session)

        assert adapter.count() == 3

        adapter.clear()

        assert adapter.count() == 0

    def test_count_returns_session_count(
        self, adapter: FileSessionAdapter
    ) -> None:
        """count() returns number of sessions."""
        assert adapter.count() == 0

        now = time.time()
        session = Session(
            id="test-session",
            repo_path="/tmp/repo",
            intention="Test",
            created_at=now,
            expires_at=now + 1800,
        )
        adapter.create(session)

        assert adapter.count() == 1
