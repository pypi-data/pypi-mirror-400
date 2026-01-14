"""
LLM Prompts and Tool Schemas.

System prompts and structured output schemas for LLM providers.
"""

from __future__ import annotations

from typing import Any

# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

CLARIFICATION_SYSTEM_PROMPT = """You are a technical clarification assistant for Preflights, a tool that helps developers make architecture decisions before coding.

Your role is to:
1. Understand the user's development intention
2. Identify what information is missing to make good technical decisions
3. Generate focused clarification questions

Guidelines:
- Ask at most 2 questions per turn
- Prefer asking a single question unless two are strictly necessary
- Never produce a long list of questions
- Stop asking questions as soon as the decision can be made explicit
- Prefer multiple-choice questions when options are clear
- Use free-text only for truly open-ended needs
- Focus on architectural impact, not implementation details
- Consider the existing codebase context provided

Question philosophy:
- Options in choice questions are examples, not recommendations
- "Other (specify)" is a first-class path, not an edge case
- If user provides an approximate category, continue the flow (do not penalize)

Output format:
Use the submit_clarification tool with:
- questions: Array of questions with id, type, question text, and options
- missing_info: Array of semantic keys describing what's still unknown (1:1 with questions)
- decision_hint: "task" (simple change), "adr" (architectural decision), or "unsure"
- progress: Estimated completion (0.0 to 1.0)

IMPORTANT:
- Each question MUST have a corresponding entry in missing_info (1:1 mapping)
- missing_info keys should be stable semantic identifiers (e.g., "auth_strategy", "db_type")
- decision_hint is purely informative - the actual decision is made deterministically by Preflights
- progress MUST be 1.0 when no missing_info remains
"""

EXTRACTION_SYSTEM_PROMPT = """You are extracting structured architecture decisions from a clarification conversation.

Given the user's intention and their answers to clarification questions, extract:
1. The primary category (Authentication, Database, Frontend, Backend, Infra, Other)
2. Key-value pairs for the decision fields

Use the submit_decision tool to provide structured output.

CRITICAL RULES:
- Category must be one of: Authentication, Database, Frontend, Backend, Infra, Other
- Fields should be relevant to the category
- If "Other (specify)" was selected, use the custom value provided by the user

ABSOLUTE PROHIBITIONS:
- Never invent, guess, or infer missing values
- Never use placeholders such as "TBD", "unknown", or similar

If insufficient information, call submit_decision with status="insufficient" and include a short reason.
Do not guess.

The deterministic MockLLMAdapter defines the reference behavior.
Your output must be compatible with its rules and constraints.

Quality over completeness:
- A patch with one concrete field is better than a patch with guessed fields
- It is valid and expected to return status="insufficient" if answers are unclear
"""


# =============================================================================
# TOOL SCHEMAS (for Anthropic Tool Use)
# =============================================================================

CLARIFICATION_TOOL_SCHEMA: dict[str, Any] = {
    "name": "submit_clarification",
    "description": "Submit clarification questions and progress status",
    "input_schema": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "description": "List of clarification questions to ask",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Unique question identifier (e.g., 'auth_strategy', 'db_type')",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["single_choice", "multi_choice", "free_text"],
                            "description": "Question type",
                        },
                        "question": {
                            "type": "string",
                            "description": "The question text to display",
                        },
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Options for choice questions (required for single_choice/multi_choice)",
                        },
                        "optional": {
                            "type": "boolean",
                            "default": False,
                            "description": "Whether this question can be skipped",
                        },
                    },
                    "required": ["id", "type", "question"],
                },
            },
            "missing_info": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Semantic keys for information still needed (1:1 with questions)",
            },
            "decision_hint": {
                "type": "string",
                "enum": ["task", "adr", "unsure"],
                "description": "Hint about decision type: task (simple), adr (architectural), unsure",
            },
            "progress": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Estimated completion progress (0.0 to 1.0)",
            },
        },
        "required": ["questions", "missing_info", "decision_hint", "progress"],
    },
}

DECISION_TOOL_SCHEMA: dict[str, Any] = {
    "name": "submit_decision",
    "description": "Submit extracted architecture decision or report insufficient information",
    "input_schema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["extracted", "insufficient"],
                "description": "Whether a decision was extracted or information is insufficient",
            },
            "category": {
                "type": "string",
                "enum": [
                    "Authentication",
                    "Database",
                    "Frontend",
                    "Backend",
                    "Infra",
                    "Other",
                ],
                "description": "Decision category (required if status=extracted)",
            },
            "fields": {
                "type": "array",
                "description": "Key-value pairs for the decision (required if status=extracted)",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Field name (e.g., 'Strategy', 'Framework')",
                        },
                        "value": {
                            "type": "string",
                            "description": "Field value",
                        },
                    },
                    "required": ["key", "value"],
                },
            },
            "reason": {
                "type": "string",
                "description": "Why information is insufficient (required if status=insufficient)",
            },
        },
        "required": ["status"],
    },
}


# =============================================================================
# CODE-SIDE VALIDATION RULES (not enforced in schema)
# =============================================================================
#
# These validations MUST be performed after receiving LLM tool call responses:
#
# CLARIFICATION responses:
# - If type in ("single_choice", "multi_choice") and options is absent/empty → REJECT
# - If type == "free_text" and options is present → IGNORE options
# - If missing_info is empty → progress MUST be 1.0 (override if needed)
# - If missing_info is not empty and progress == 1.0 → clamp to 0.99 + warning
#
# DECISION responses:
# - If status == "extracted" → category and fields MUST be present
# - If status == "insufficient" → reason MUST be present
# - If status == "extracted" and fields is empty → treat as "insufficient"
#
# =============================================================================


# =============================================================================
# FUNCTION SCHEMAS (for OpenAI Function Calling)
# =============================================================================


def get_clarification_function_schema() -> dict[str, Any]:
    """Get OpenAI-compatible function schema for clarification."""
    return {
        "name": "submit_clarification",
        "description": CLARIFICATION_TOOL_SCHEMA["description"],
        "parameters": CLARIFICATION_TOOL_SCHEMA["input_schema"],
    }


def get_decision_function_schema() -> dict[str, Any]:
    """Get OpenAI-compatible function schema for decision extraction."""
    return {
        "name": "submit_decision",
        "description": DECISION_TOOL_SCHEMA["description"],
        "parameters": DECISION_TOOL_SCHEMA["input_schema"],
    }
