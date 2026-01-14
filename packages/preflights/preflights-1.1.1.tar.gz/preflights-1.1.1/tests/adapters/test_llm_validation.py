"""
Tests for LLM Response Validation.

These tests ensure the validation layer enforces behavioral invariants
defined in mock-llm-spec.md.
"""

import pytest

from preflights.adapters.llm_validation import (
    ALLOWED_DECISION_CATEGORIES,
    LLMValidationError,
    MAX_QUESTIONS_PER_TURN,
    normalize_category,
    validate_and_repair_clarification,
    validate_and_repair_decision,
    validate_clarification_response,
    validate_clarification_strict,
    validate_decision_response,
    validate_decision_strict,
)


class TestClarificationMaxQuestions:
    """Test max 2 questions per turn invariant."""

    def test_two_questions_allowed(self):
        """Two questions should pass validation."""
        response = {
            "questions": [
                {"id": "q1", "type": "free_text", "question": "Q1?"},
                {"id": "q2", "type": "free_text", "question": "Q2?"},
            ],
            "missing_info": ["q1", "q2"],
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        result = validate_clarification_response(response, strict=False)
        assert result.valid
        assert len(result.data["questions"]) == 2

    def test_three_questions_truncated_in_repair_mode(self):
        """Three questions should be truncated to 2 in repair mode."""
        response = {
            "questions": [
                {"id": "q1", "type": "free_text", "question": "Q1?"},
                {"id": "q2", "type": "free_text", "question": "Q2?"},
                {"id": "q3", "type": "free_text", "question": "Q3?"},
            ],
            "missing_info": ["q1", "q2", "q3"],
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        result = validate_clarification_response(response, strict=False)
        assert result.repaired
        assert len(result.data["questions"]) == MAX_QUESTIONS_PER_TURN

    def test_three_questions_raises_in_strict_mode(self):
        """Three questions should raise in strict mode."""
        response = {
            "questions": [
                {"id": "q1", "type": "free_text", "question": "Q1?"},
                {"id": "q2", "type": "free_text", "question": "Q2?"},
                {"id": "q3", "type": "free_text", "question": "Q3?"},
            ],
            "missing_info": ["q1", "q2", "q3"],
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        with pytest.raises(LLMValidationError) as exc_info:
            validate_clarification_strict(response)
        assert exc_info.value.code == "TOO_MANY_QUESTIONS"


class TestClarificationQuestionsMissingInfoMatch:
    """Test len(questions) == len(missing_info) invariant."""

    def test_matching_counts_valid(self):
        """Matching counts should pass validation."""
        response = {
            "questions": [{"id": "q1", "type": "free_text", "question": "Q1?"}],
            "missing_info": ["q1"],
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        result = validate_clarification_response(response, strict=False)
        assert result.valid

    def test_mismatch_repaired(self):
        """Mismatch should be repaired by regenerating missing_info."""
        response = {
            "questions": [
                {"id": "auth_strategy", "type": "free_text", "question": "Q1?"},
            ],
            "missing_info": ["wrong1", "wrong2"],  # Mismatch!
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        result = validate_clarification_response(response, strict=False)
        assert result.repaired
        assert result.data["missing_info"] == ["auth_strategy"]


class TestClarificationQCMOptions:
    """Test QCM questions must have options."""

    def test_single_choice_with_options_valid(self):
        """single_choice with options should pass."""
        response = {
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "question": "Q1?",
                    "options": ["A", "B", "C"],
                }
            ],
            "missing_info": ["q1"],
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        result = validate_clarification_response(response, strict=False)
        assert result.valid

    def test_single_choice_without_options_repaired(self):
        """single_choice without options should be converted to free_text."""
        response = {
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "question": "Q1?",
                    # No options!
                }
            ],
            "missing_info": ["q1"],
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        result = validate_clarification_response(response, strict=False)
        assert result.repaired
        assert result.data["questions"][0]["type"] == "free_text"

    def test_multi_choice_with_one_option_repaired(self):
        """multi_choice with < 2 options should be converted to free_text."""
        response = {
            "questions": [
                {
                    "id": "q1",
                    "type": "multi_choice",
                    "question": "Q1?",
                    "options": ["Only one"],  # Need at least 2
                }
            ],
            "missing_info": ["q1"],
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        result = validate_clarification_response(response, strict=False)
        assert result.repaired
        assert result.data["questions"][0]["type"] == "free_text"


class TestClarificationProgressInvariant:
    """Test progress invariant: progress == 1.0 iff missing_info empty."""

    def test_empty_missing_info_forces_progress_1(self):
        """Empty missing_info should force progress to 1.0."""
        response = {
            "questions": [],
            "missing_info": [],
            "decision_hint": "task",
            "progress": 0.5,  # Wrong!
        }
        result = validate_clarification_response(response, strict=False)
        assert result.repaired
        assert result.data["progress"] == 1.0

    def test_non_empty_missing_info_clamps_progress(self):
        """Non-empty missing_info with progress=1.0 should be clamped."""
        response = {
            "questions": [{"id": "q1", "type": "free_text", "question": "Q1?"}],
            "missing_info": ["q1"],
            "decision_hint": "unsure",
            "progress": 1.0,  # Wrong - still have missing info!
        }
        result = validate_clarification_response(response, strict=False)
        assert result.repaired
        assert result.data["progress"] == 0.99


class TestDecisionStatus:
    """Test status field validation."""

    def test_extracted_with_valid_data(self):
        """status=extracted with valid category and fields should pass."""
        response = {
            "status": "extracted",
            "category": "Authentication",
            "fields": [{"key": "Strategy", "value": "OAuth"}],
        }
        result = validate_decision_response(response, strict=False)
        assert result.valid
        assert result.data["status"] == "extracted"

    def test_insufficient_with_reason(self):
        """status=insufficient with reason should pass."""
        response = {
            "status": "insufficient",
            "reason": "User did not specify auth provider",
        }
        result = validate_decision_response(response, strict=False)
        assert result.valid
        assert result.data["status"] == "insufficient"

    def test_insufficient_without_reason_repaired(self):
        """status=insufficient without reason should be repaired."""
        response = {
            "status": "insufficient",
            # No reason!
        }
        result = validate_decision_response(response, strict=False)
        assert result.repaired
        assert result.data["reason"] is not None

    def test_missing_status_inferred(self):
        """Missing status should be inferred from other fields."""
        response = {
            "category": "Database",
            "fields": [{"key": "Type", "value": "PostgreSQL"}],
            # No status!
        }
        result = validate_decision_response(response, strict=False)
        assert result.repaired
        assert result.data["status"] == "extracted"


class TestDecisionPlaceholders:
    """Test placeholder detection in decision fields."""

    def test_tbd_placeholder_rejected(self):
        """TBD placeholder should be rejected."""
        response = {
            "status": "extracted",
            "category": "Authentication",
            "fields": [{"key": "Strategy", "value": "TBD"}],
        }
        result = validate_decision_response(response, strict=False)
        assert result.repaired
        # Field should be removed, leading to insufficient
        assert result.data["status"] == "insufficient"

    def test_unknown_placeholder_rejected(self):
        """'unknown' placeholder should be rejected."""
        response = {
            "status": "extracted",
            "category": "Database",
            "fields": [{"key": "Type", "value": "unknown"}],
        }
        result = validate_decision_response(response, strict=False)
        assert result.repaired
        assert result.data["status"] == "insufficient"

    def test_todo_placeholder_rejected(self):
        """TODO placeholder should be rejected."""
        response = {
            "status": "extracted",
            "category": "Frontend",
            "fields": [{"key": "Framework", "value": "TODO: decide later"}],
        }
        result = validate_decision_response(response, strict=False)
        assert result.repaired
        assert result.data["status"] == "insufficient"

    def test_valid_value_accepted(self):
        """Valid concrete value should be accepted."""
        response = {
            "status": "extracted",
            "category": "Backend",
            "fields": [{"key": "Framework", "value": "FastAPI"}],
        }
        result = validate_decision_response(response, strict=False)
        assert result.valid
        assert result.data["fields"][0]["value"] == "FastAPI"


class TestCategoryNormalization:
    """Test category alias normalization."""

    def test_infrastructure_normalized_to_infra(self):
        """'Infrastructure' should be normalized to 'Infra'."""
        assert normalize_category("Infrastructure") == "Infra"

    def test_auth_normalized_to_authentication(self):
        """'Auth' should be normalized to 'Authentication'."""
        assert normalize_category("Auth") == "Authentication"

    def test_db_normalized_to_database(self):
        """'DB' should be normalized to 'Database'."""
        assert normalize_category("DB") == "Database"

    def test_valid_category_unchanged(self):
        """Valid category should remain unchanged."""
        for cat in ALLOWED_DECISION_CATEGORIES:
            assert normalize_category(cat) == cat

    def test_normalization_applied_in_decision_validation(self):
        """Category normalization should be applied during validation."""
        response = {
            "status": "extracted",
            "category": "Infrastructure",  # Should become "Infra"
            "fields": [{"key": "Hosting", "value": "AWS"}],
        }
        result = validate_decision_response(response, strict=False)
        assert result.data["category"] == "Infra"


class TestConvenienceFunctions:
    """Test convenience functions for production use."""

    def test_validate_and_repair_clarification_returns_dict(self):
        """validate_and_repair_clarification should return usable data."""
        response = {
            "questions": [{"id": "q1", "type": "free_text", "question": "Q1?"}],
            "missing_info": ["q1"],
            "decision_hint": "unsure",
            "progress": 0.5,
        }
        result = validate_and_repair_clarification(response)
        assert isinstance(result, dict)
        assert "questions" in result

    def test_validate_and_repair_decision_returns_dict(self):
        """validate_and_repair_decision should return usable data."""
        response = {
            "status": "extracted",
            "category": "Authentication",
            "fields": [{"key": "Strategy", "value": "OAuth"}],
        }
        result = validate_and_repair_decision(response)
        assert isinstance(result, dict)
        assert result["status"] == "extracted"
