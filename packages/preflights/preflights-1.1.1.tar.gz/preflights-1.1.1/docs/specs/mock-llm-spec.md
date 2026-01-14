# MockLLMAdapter Specification

**Product:** Preflights
**Version:** 1.0.0
**Purpose:** Deterministic reference behavior + fallback for LLM interactions
**Philosophy:** Reduce ambiguity, not increase cognitive load

---

## 1. Role & Objectives

### 1.1 What the Mock Is

The MockLLMAdapter is:
- **Deterministic**: same inputs → same outputs, always
- **Technology-aware**: recognizes categories and decision points
- **Behavioral reference**: defines the correct clarification workflow
- **Fallback**: works when real LLM is unavailable

### 1.2 What the Mock Is NOT

The mock is NOT:
- A simulator of real LLM knowledge
- A technology recommender
- A domain expert

### 1.3 Primary Goal

Surface implicit decisions and eliminate ambiguity with **minimal questions** while producing **valid DecisionPatch** artifacts.

---

## 2. Core Constraints (MANDATORY)

### 2.1 Determinism

Given the same inputs, the adapter MUST always return:
- The same questions
- In the same order
- With the same IDs
- With the same `missing_info`
- With the same `decision_hint`

**No randomness. No time. No I/O.**

### 2.2 Question Budget (CRITICAL UX RULE)

| Rule | Value |
|------|-------|
| Questions per turn | 1-2 max |
| Total turns | 2-3 max |
| Default | 1 question |

**Never produce a long questionnaire.**
**Never ask questions "just in case".**

This must feel like a short conversation, not a form.

---

## 3. Hybrid Flow (Normative)

The mock uses a **two-phase hybrid approach**:

### 3.1 Phase 1: Category Detection

**Turn 1** — Always ask ONE generic question to identify scope:

```
"What type of change is this?"
Options: [Frontend, Backend, Database, Authentication, Infra, Other (specify)]
```

Purpose:
- Detect which schema category applies
- Determine if ADR is needed (structural) or just TASK (local)

**UX Tolerance Rule:**
If the user selects an incorrect or approximate category, this is acceptable.
The mock MUST prioritize flow continuation over category accuracy.
A user who picks "Backend" when they meant "Infra" should not be penalized.

### 3.2 Phase 2: Field Collection (if needed)

**Turn 2** — If a known category is detected, ask ONE targeted question:

| Category | Question | Options |
|----------|----------|---------|
| Authentication | "Which authentication approach?" | OAuth, Email/Password, Magic Link, Other |
| Database | "Which database type?" | PostgreSQL, MySQL, MongoDB, Other |
| Frontend | "Which framework?" | React, Vue, Svelte, Other |
| Backend | "Which API style?" | REST, GraphQL, gRPC, Other |
| Infra | "Which hosting approach?" | Cloud, Self-hosted, Serverless, Other |

**Then stop.**

**LOCKED DESIGN DECISION #1:**
The mock MUST NEVER ask more than ONE targeted field question per turn.
Even if the category has multiple fields (e.g., Authentication has Strategy + Library),
only ONE field is collected per turn. This prevents questionnaire UX.

### 3.3 Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Turn 1: Generic Category Question                           │
│ "What type of change is this?"                              │
│ → User answers: "Authentication"                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Turn 2: Targeted Field Question (if category recognized)    │
│ "Which authentication approach?"                            │
│ → User answers: "OAuth"                                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Done: Extract DecisionPatch                                 │
│ category="Authentication", fields=[("Strategy", "OAuth")]   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Question Types

### 4.1 Generic Question (Phase 1)

```python
Question(
    id="change_category",
    type="single_choice",
    question="What type of change is this?",
    options=("Frontend", "Backend", "Database", "Authentication",
             "Infra", "Other (specify)"),
)
```

Purpose: Route to the correct schema category.

### 4.2 Targeted Questions (Phase 2)

One question per category, focused on the **primary field**:

```python
# Authentication
Question(
    id="auth_strategy",
    type="single_choice",
    question="Which authentication approach?",
    options=("OAuth", "Email/Password", "Magic Link", "Other (specify)"),
)

# Database
Question(
    id="db_type",
    type="single_choice",
    question="Which database type?",
    options=("PostgreSQL", "MySQL", "MongoDB", "Other (specify)"),
)
```

### 4.3 "Other (specify)" Rule

All `single_choice` questions include `"Other (specify)"` as the last option.

When selected:
- The associated `{qid}__other` free-text field becomes required
- User provides custom value
- Mock uses that value in the DecisionPatch

**First-Class Path:**
Phase 2 options are **examples, not recommendations**.
Selecting "Other (specify)" is a **first-class path**, not an edge case.

The mock MUST NOT bias toward predefined options:
- "Other (specify)" should be equally visible
- Custom values are equally valid for DecisionPatch generation
- No implicit preference for listed options

---

## 5. DecisionPatch Extraction (CRITICAL)

### 5.1 Schema Mapping

The mock uses a fixed mapping from category to expected fields:

| Category | Primary Field | Secondary Field |
|----------|---------------|-----------------|
| Authentication | Strategy | Library |
| Database | Type | ORM |
| Frontend | Framework | Styling |
| Backend | Framework | API_Style |
| Infra | Hosting | CI_CD |
| Other | Description | — |

### 5.2 Extraction Rules

**Rule 1: No TBD values**

If user doesn't provide a concrete value → **do not generate a patch with placeholders**.
Return `None` and continue clarification.

**Rule 2: Resolve "Other (specify)"**

```python
def resolve_value(answers: dict, qid: str, default: str) -> str:
    value = answers.get(qid, default)
    if value == "Other (specify)":
        return answers.get(f"{qid}__other", default)
    return value
```

**Rule 3: Minimal valid patch**

Only include fields that have concrete answers:

```python
# Good: concrete value
DecisionPatch(
    category="Authentication",
    fields=(("Strategy", "OAuth"),),
)

# Bad: placeholder
DecisionPatch(
    category="Authentication",
    fields=(("Strategy", "TBD"),),  # ❌ Never do this
)
```

### 5.3 Extraction Algorithm

```python
def extract_decision_patch(intention, answers, config) -> DecisionPatch | None:
    # 1. Determine category
    category = resolve_value(answers, "change_category", None)
    if category is None:
        return None  # Need more clarification

    # 2. Get field mapping for category
    field_map = CATEGORY_FIELD_MAP.get(category)
    if field_map is None:
        # Unknown category → use "Other" with description
        desc = answers.get("description", intention)
        return DecisionPatch(category="Other", fields=(("Description", desc),))

    # 3. Extract fields with concrete values only
    fields = []
    for field_name, question_id in field_map.items():
        value = resolve_value(answers, question_id, None)
        if value is not None and value != "":
            fields.append((field_name, value))

    # 4. Must have at least one field
    if not fields:
        return None  # Need more clarification

    return DecisionPatch(category=category, fields=tuple(fields))
```

---

## 6. decision_hint Semantics

`decision_hint` is **informational only**. Core makes the final decision.

| Hint | When to use |
|------|-------------|
| `adr` | Category is structural (Auth, Database, Infra) |
| `task` | Category is local (Frontend component, small Backend change) |
| `unsure` | Cannot determine from answers |

**Backend Nuance:**
Backend defaults to `adr` only when it affects API shape or cross-module contracts.
Isolated backend changes (e.g., refactoring a single service) may resolve to `task`.
The mock uses `adr` as default for Backend, but Core may override based on scope analysis.

```python
ADR_CATEGORIES = {"Authentication", "Database", "Infra"}
ADR_LEANING_CATEGORIES = {"Backend"}  # Default adr, but may be task
TASK_CATEGORIES = {"Frontend"}

def compute_hint(category: str) -> str:
    if category in ADR_CATEGORIES:
        return "adr"
    if category in ADR_LEANING_CATEGORIES:
        return "adr"  # Default, Core may override
    if category in TASK_CATEGORIES:
        return "task"
    return "unsure"
```

---

## 7. missing_info Semantics

`missing_info` tracks **conceptual gaps**, not question text.

| Key | Meaning |
|-----|---------|
| `change_category` | Don't know what type of change |
| `auth_strategy` | Auth category detected, need strategy |
| `db_type` | Database category detected, need type |
| `description` | Other category, need description |

**Rules:**
- One `missing_info` item = one blocking ambiguity
- Do NOT include `__other` fields in `missing_info`
- Length of `missing_info` should equal number of unanswered required questions

---

## 8. progress Calculation

`progress` is proportional to resolved `missing_info`.

**Rule:**
```python
def compute_progress(total_expected: int, remaining_missing: int) -> float:
    if remaining_missing == 0:
        return 1.0  # MUST be 1.0 when no missing_info remains
    return (total_expected - remaining_missing) / total_expected
```

**Simplified implementation:**

| State | Progress |
|-------|----------|
| Phase 1 not answered | 0.0 |
| Phase 1 answered, Phase 2 pending | 0.5 |
| All answered, ready to extract | 1.0 |

If `missing_info` is empty, `progress` MUST be `1.0`.

---

## 9. Keyword Detection (Shortcut)

The mock MAY skip Phase 1 if intention contains clear keywords:

| Keywords in intention | Skip to |
|-----------------------|---------|
| `auth`, `login`, `oauth`, `jwt` | Phase 2: Authentication |
| `database`, `db`, `postgres`, `mysql` | Phase 2: Database |
| `frontend`, `ui`, `react`, `component` | Phase 2: Frontend |
| `api`, `endpoint`, `backend` | Phase 2: Backend |
| `deploy`, `docker`, `ci`, `infra` | Phase 2: Infra |

This preserves backward compatibility with existing tests.

---

## 9. Behavioral Contract

### 9.1 generate_questions()

```python
def generate_questions(
    intention: str,
    heuristics_config: HeuristicsConfig,
    context: LLMContext | None,
    session_state: SessionSnapshot | None,
) -> LLMResponse:
    """
    Returns:
    - questions: 1-2 questions max
    - missing_info: semantic keys for unanswered questions
    - decision_hint: "task" | "adr" | "unsure"
    - progress: 0.0 to 1.0
    """
```

### 9.2 extract_decision_patch()

```python
def extract_decision_patch(
    intention: str,
    answers: dict[str, str | tuple[str, ...]],
    heuristics_config: HeuristicsConfig,
) -> DecisionPatch | None:
    """
    Returns:
    - DecisionPatch with valid category + fields
    - None if cannot extract (need more clarification)

    Never returns:
    - Patch with TBD/placeholder values
    - Patch with invalid category
    """
```

---

## 10. Test Compatibility

### 10.1 Preserved Question IDs

For backward compatibility, keep these IDs:
- `auth_strategy`, `auth_library`
- `db_type`, `db_orm`
- `frontend_framework`, `styling`
- `change_category`, `description`

### 10.2 Migration Path

1. Existing keyword-based tests continue to work
2. New tests use hybrid flow
3. Question count reduced from 4+ to 1-2

---

## 11. Locked Design Decisions

### DECISION #1: One Field Per Turn
(See Section 3.2)

The mock MUST NEVER ask more than ONE targeted field question per turn.

### DECISION #2: Valid Outcome Without Patch

**It is a valid and expected outcome for the mock to stop without producing a DecisionPatch.**

This protects:
- UX quality (no forced answers)
- ADR integrity (no TBD/placeholder values)
- Preflights philosophy (clarification > completion)

When the mock returns `None` from `extract_decision_patch()`:
- Application continues clarification
- User is not penalized
- Flow remains intact

---

## 12. Success Criteria

The MockLLMAdapter is correct if:

1. **Prevents implicit decisions**: AI agents cannot decide architecture alone
2. **Forces explicit choices**: User must acknowledge decisions
3. **Produces valid patches**: DecisionPatch always conforms to schema (or None)
4. **Stays minimal**: 1-2 questions max per turn
5. **Works universally**: Not tied to specific tech stack
6. **Remains deterministic**: Same inputs → same outputs
7. **Accepts incomplete flows**: Stopping without a patch is valid

---

## 13. Guiding Principle (DO NOT VIOLATE)

> The MockLLMAdapter must reduce ambiguity, not increase cognitive load.

If you must choose between:
- Asking another question
- Stopping with partial clarity

**Stop.**

A valid partial patch is better than a complete questionnaire.

---

## 14. Governance Rule (NORMATIVE)

**The MockLLMAdapter is the source of truth for behavioral contracts.**

### Rule 1: Prompt Alignment

System prompts are normative.
Any change to question budget or clarification flow MUST be reflected in:
1. This spec (`mock-llm-spec.md`)
2. All LLM system prompts (`llm_prompts.py`)

### Rule 2: Spec-First Changes

When modifying clarification behavior:
1. Update `mock-llm-spec.md` first
2. Update `llm_prompts.py` to match
3. Update `mock_llm.py` implementation
4. Update tests

### Rule 3: Mock = Reference

Real LLM adapters (Anthropic, OpenAI, OpenRouter) MUST produce outputs
that are structurally compatible with MockLLMAdapter outputs.

The mock defines:
- Question budget (1-2 per turn)
- Progress semantics
- DecisionPatch validity rules
- Acceptable outcomes (including None)

LLM prompts instruct the model to behave accordingly.
