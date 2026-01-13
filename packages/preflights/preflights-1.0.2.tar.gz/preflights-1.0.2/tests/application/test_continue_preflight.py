"""Tests for continue_preflight() function.

Tests the second public API: continuing a preflight session.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from preflights.adapters.fixed_clock import FixedClockProvider
from preflights.adapters.mock_llm import MockLLMAdapter
from preflights.application.preflights_app import PreflightsApp
from preflights.application.types import AppErrorCode


class TestContinuePreflightBasic:
    """Basic continue_preflight tests."""

    def test_continue_preflight_with_valid_session(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """continue_preflight works with a valid session and returns valid status."""
        # Given: A started session with answered questions
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}

        # When: continue_preflight is called
        result = app.continue_preflight(session_id, answers)

        # Then: A valid status is returned
        valid_statuses = ("needs_more_answers", "needs_clarification", "completed")
        assert result.status in valid_statuses, (
            f"Expected status in {valid_statuses}, got '{result.status}'. "
            f"Error: {result.error.message if result.error else 'None'}"
        )


class TestContinuePreflightSessionValidation:
    """Session validation tests."""

    def test_continue_preflight_rejects_unknown_session(
        self,
        app: PreflightsApp,
    ) -> None:
        """continue_preflight returns error for unknown session."""
        # When: continue_preflight is called with unknown session ID
        result = app.continue_preflight("unknown-session-id", {})

        # Then: SESSION_NOT_FOUND error with recovery hint
        assert result.status == "error"
        assert result.error is not None
        assert result.error.code == AppErrorCode.SESSION_NOT_FOUND
        assert result.error.recovery_hint is not None


class TestContinuePreflightAnswerMerging:
    """Answer merging tests."""

    def test_answers_are_accumulated(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Answers from multiple calls are accumulated."""
        from preflights.application.types import Question

        # Given: A session with two required questions
        llm_adapter.set_questions([
            Question(id="q1", type="single_choice", question="First question", options=("a", "b"), optional=False),
            Question(id="q2", type="single_choice", question="Second question", options=("c", "d"), optional=False),
        ])
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id

        # When: Only first question is answered
        result1 = app.continue_preflight(session_id, {"q1": "a"})

        # Then: needs_more_answers with only q2 remaining
        assert result1.status == "needs_more_answers", (
            f"Expected needs_more_answers after partial answer, got {result1.status}"
        )
        assert result1.questions is not None
        unanswered_ids = [q.id for q in result1.questions]
        assert "q2" in unanswered_ids, "q2 should still need an answer"
        assert "q1" not in unanswered_ids, "q1 should not be re-asked"

        # When: Second question is answered (without re-providing q1)
        result2 = app.continue_preflight(session_id, {"q2": "c"})

        # Then: Flow progresses past needs_more_answers
        assert result2.status != "needs_more_answers", (
            f"Both questions answered, should not need more answers. Status: {result2.status}"
        )

    def test_multi_choice_answers_accepted(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Multi-choice answers with list format are accepted."""
        from preflights.application.types import Question

        # Given: A session with a multi-choice question
        llm_adapter.set_questions([
            Question(
                id="multi_q",
                type="multi_choice",
                question="Select features",
                options=("feature1", "feature2", "feature3"),
                min_selections=1,
                max_selections=3,
                optional=False,
            )
        ])
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id

        # When: Answer with list format
        result = app.continue_preflight(session_id, {"multi_q": ["feature1", "feature2"]})

        # Then: No INVALID_ANSWER error
        if result.status == "error":
            assert result.error.code != "INVALID_ANSWER", (
                f"Multi-choice list format should be accepted: {result.error.message}"
            )


class TestContinuePreflightNeedsMoreAnswers:
    """Tests for needs_more_answers status."""

    def test_returns_needs_more_answers_when_incomplete(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Returns needs_more_answers when required questions unanswered."""
        from preflights.application.types import Question

        # Given: A session with two required questions
        llm_adapter.set_questions([
            Question(id="q1", type="single_choice", question="Question 1", options=("a", "b"), optional=False),
            Question(id="q2", type="single_choice", question="Question 2", options=("c", "d"), optional=False),
        ])
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id

        # When: Only first question answered
        result = app.continue_preflight(session_id, {"q1": "a"})

        # Then: needs_more_answers with q2 remaining
        assert result.status == "needs_more_answers"
        assert result.questions is not None
        assert len(result.questions) == 1
        assert result.questions[0].id == "q2"

    def test_optional_questions_not_required(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
        llm_adapter: MockLLMAdapter,
    ) -> None:
        """Optional questions don't block completion."""
        from preflights.application.types import Question

        # Given: A session with one required and one optional question
        llm_adapter.set_questions([
            Question(id="required_q", type="single_choice", question="Required", options=("a", "b"), optional=False),
            Question(id="optional_q", type="free_text", question="Optional", optional=True),
        ])
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id

        # When: Only required question answered
        result = app.continue_preflight(session_id, {"required_q": "a"})

        # Then: Flow progresses (not blocked by optional)
        assert result.status != "needs_more_answers"


class TestContinuePreflightCompleted:
    """Tests for completed status."""

    def test_completed_returns_artifacts(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """Completed result includes artifact paths."""
        # Given: A session answering all questions to completion
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}

        # When: Session is completed (may need multiple turns)
        result = app.continue_preflight(session_id, answers)
        turns = 0
        while result.status in ("needs_clarification", "needs_more_answers") and result.questions and turns < 10:
            new_answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = app.continue_preflight(session_id, new_answers)
            turns += 1

        # Then: Completed with artifacts
        assert result.status == "completed", f"Expected completed, got {result.status}. Error: {result.error}"
        assert result.artifacts is not None, "Completed result must have artifacts"
        assert result.artifacts.task_path is not None, "Must have task_path"

    def test_completed_closes_session(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """Session is deleted after completion."""
        # Given: A completed session
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id

        # Verify session exists
        check_result = app.continue_preflight(session_id, {})
        assert check_result.status != "error" or check_result.error.code != "SESSION_NOT_FOUND", (
            "Session must exist after start"
        )

        # Complete the session
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)
        turns = 0
        while result.status in ("needs_clarification", "needs_more_answers") and result.questions and turns < 10:
            new_answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = app.continue_preflight(session_id, new_answers)
            turns += 1
        assert result.status == "completed", f"Expected completed, got {result.status}. Error: {result.error}"

        # When: Attempt to continue after completion
        post_complete_result = app.continue_preflight(session_id, {})

        # Then: SESSION_NOT_FOUND
        assert post_complete_result.status == "error", "Continuing closed session should error"
        assert post_complete_result.error.code == AppErrorCode.SESSION_NOT_FOUND, (
            f"Expected SESSION_NOT_FOUND after completion, got {post_complete_result.error.code}"
        )


class TestContinuePreflightNeedsClarification:
    """Tests for needs_clarification status."""

    def test_needs_clarification_returns_questions(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """needs_clarification includes follow-up questions."""
        # Given: A session with answered initial questions
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}

        # When: continue_preflight is called
        result = app.continue_preflight(session_id, answers)

        # Then: If needs_clarification, questions have required fields
        if result.status == "needs_clarification":
            assert result.questions is not None
            assert len(result.questions) >= 1
            for q in result.questions:
                assert q.id is not None
                assert q.question is not None

    def test_clarification_questions_are_new(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """Clarification questions are different from initial questions."""
        # Given: A started session with initial questions
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id
        initial_question_ids = {q.id for q in start_result.questions}

        # When: All initial questions are answered
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)

        # Then: Clarification questions are new (not repeats)
        if result.status == "needs_clarification":
            assert result.questions is not None
            new_question_ids = {q.id for q in result.questions}
            repeated = new_question_ids & initial_question_ids
            assert not repeated, f"Questions should not be re-asked: {repeated}"


class TestContinuePreflightError:
    """Tests for error status."""

    def test_error_includes_recovery_hint(
        self,
        app: PreflightsApp,
    ) -> None:
        """Error responses include recovery hint."""
        # When: continue_preflight with unknown session
        result = app.continue_preflight("unknown-session", {})

        # Then: Error with recovery hint
        assert result.status == "error"
        assert result.error is not None
        assert result.error.recovery_hint is not None


class TestContinuePreflightMultiTurn:
    """Multi-turn conversation flow tests."""

    def test_full_multi_turn_flow(
        self,
        app: PreflightsApp,
        valid_intention: str,
        valid_repo_path: str,
    ) -> None:
        """Complete multi-turn conversation flow reaches completed state."""
        # Given: A started session
        start_result = app.start_preflight(valid_intention, valid_repo_path)
        session_id = start_result.session_id
        assert start_result.questions, "Must have initial questions"

        # When: Questions are answered until completion
        turns = 0
        max_turns = 10
        answers = {q.id: q.options[0] if q.options else "answer" for q in start_result.questions if not q.optional}
        result = app.continue_preflight(session_id, answers)
        turns += 1

        while result.status in ("needs_clarification", "needs_more_answers") and turns < max_turns:
            assert result.questions, f"Must have questions if status is {result.status}"
            new_answers = {q.id: q.options[0] if q.options else "yes" for q in result.questions}
            result = app.continue_preflight(session_id, new_answers)
            turns += 1

        # Then: Completed within reasonable turns
        assert result.status == "completed", f"Expected completed, got {result.status}. Error: {result.error}"
        assert turns <= 5, f"Flow took {turns} turns, expected ≤5 for simple intention"
        assert result.artifacts is not None, "Completed must have artifacts"
