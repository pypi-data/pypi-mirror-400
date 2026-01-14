# MASTER DESIGN: PREFLIGHTS

**Product:** Preflights
**Website:** preflights.org
**Version:** 1.0.0
**Philosophy:** "Code Less, Specify More."
**Role:** Clarification and decision capture engine for AI-assisted development.

---

## 1. The Problem

AI coding agents (Claude Code, Cursor, Windsurf) implement extremely fast.
The problem is not speed, but **what gets implemented without being explicitly decided**.

This produces:
- implicit architectural decisions
- multi-file inconsistencies
- rework disguised as rapid iterations
- technical debt that is hard to trace

**The real problem:**
a lack of explicit architectural context and confusion between long-term decisions and one-off intentions.

---

## 2. The Proposal

Preflights explicitly separates three activities that AI tools conflate:
1. **Decide** (architecture)
2. **Specify** (implementable intention)
3. **Implement** (code)

Preflights does not generate code.
It forces clarification, documents decisions, and produces clear briefs for implementation by an AI agent.

---

## 3. Global Conceptual Model

### 3.1 The Three Artifacts

```
┌──────────────────────────────────────────────┐
│ ADR — Architecture Decision Records          │
│ • Structural decisions                       │
│ • Long-lasting                               │
│ • Few in number (but historical)             │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│ TASK — Execution Briefs                      │
│ • One-off intentions                         │
│ • Local scope                                │
│ • Always implementable                       │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│ CODE                                         │
│ • Concrete implementation                    │
│ • Respects ADR + TASK                        │
└──────────────────────────────────────────────┘
```

### 3.2 Nature Distinction

| Artifact | Duration | Scope | Reversibility | Role |
|----------|----------|-------|---------------|------|
| ADR | Long-term | Global | Difficult | Decide |
| TASK | Short-term | Local | N/A | Specify |
| Code | Variable | Technical | Total | Implement |

**Heuristic rule:**
If changing implies a migration, a redesign, or affects many parts of the code → ADR.
Otherwise → TASK.

---

## 4. Artifact Organization

### 4.1 Canonical Directory Structure

```
docs/
├── ARCHITECTURE_STATE.md      # Generated projection (quick reference)
├── CURRENT_TASK.md            # Active task (mutable, current scope)
├── adr/
│   ├── 001_initial_architecture.md
│   ├── 042_authentication_strategy.md
│   └── ...
└── archive/
    └── task/
        ├── 001_initial_setup.md
        └── ...
```

### 4.2 Rules

- ADR files are **immutable** and numerically ordered
- Each ADR represents a **complete snapshot** of the architecture at a point in time
- `ARCHITECTURE_STATE.md` is an **automatically generated projection**
- Only one active TASK at a time: `CURRENT_TASK.md`
- The old TASK is automatically archived when a new one is created

---

## 5. ADR Format

Each ADR contains two sections:
- **PART 1: ARCHITECTURE SNAPSHOT** — Quick reference (machine + human)
- **PART 2: DECISION DETAILS** — Justification and audit

### 5.1 ADR Template

```markdown
# ADR-XXX: [Decision Title]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 1: ARCHITECTURE SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Version:** XXX
**UID:** YYYYMMDDTHHMMSS.mmmZ
**Date (UTC):** YYYY-MM-DD
**Previous UID:** YYYYMMDDTHHMMSS.mmmZ | None

## Changes in this version
- [Added/Modified/Removed]: [Description]

## CURRENT ARCHITECTURE STATE

### Frontend
- Framework: [Decision] (ADR-XXX)
- State Management: [Decision] (ADR-XXX)
...

### Backend
- Language: [Decision] (ADR-XXX)
- Framework: [Decision] (ADR-XXX)
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 2: DECISION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Context
[Why is this decision needed?]

## Decision
[What did we decide?]

## Rationale
[Why this decision?]

## Alternatives Considered
...

## Consequences
...
```

### 5.2 Deterministic Generation

ADR snapshots are rebuilt deterministically:
- From the previous snapshot + diff of the current decision
- Automatic validation of categories and fields
- Rejection in case of inconsistency

---

## 6. TASK — Execution Brief

A `TASK.md` describes **what needs to be implemented now**.

Required content:
- Objective
- Context (applicable ADRs)
- Allowlist / Forbidden list
- Technical constraints
- Acceptance Criteria

---

## 7. Technical Architecture

### 7.1 Code Structure

```
preflights/
├── core/           # Pure logic (stateless, deterministic, NO I/O)
├── application/    # Orchestration (PreflightsApp, ports)
├── adapters/       # I/O (filesystem, LLM, sessions, UID, clock)
├── cli/            # CLI interface (Click)
└── mcp/            # MCP Server
```

### 7.2 Ports & Adapters

| Layer | Responsibility | I/O |
|-------|----------------|-----|
| `core/` | Pure business logic | **NO** |
| `application/` | Orchestration | Via adapters |
| `adapters/` | I/O (FS, LLM, UID, Clock) | **YES** |
| `cli/` | User interface | Via adapters |
| `mcp/` | JSON-RPC MCP | Via adapters |

### 7.3 Defined Ports

| Port | Responsibility |
|------|----------------|
| `LLMPort` | Question generation, DecisionPatch extraction |
| `SessionPort` | Session storage with TTL |
| `FilesystemPort` | Artifact read/write |
| `UIDProviderPort` | Identifier generation |
| `ClockPort` | Timestamping |
| `FileContextBuilderPort` | Repository scanning |
| `ConfigLoaderPort` | Configuration loading |

### 7.4 Absolute Rule: Pure Core

```python
# FORBIDDEN in core/
datetime.now()          # Non-deterministic
open("file.txt")        # I/O
uuid.uuid4()            # Random
import anthropic        # External service
```

---

## 8. Canonical Workflow

### 8.1 Golden Path — CLI First

```bash
pf start "Add authentication"
# Interactive clarification
# → CURRENT_TASK.md generated
# → ADR generated if structural decision
```

### 8.2 Fallback — MCP

If the user starts in Claude Code:
- Claude detects an ambiguous request
- Calls `require_clarification` via MCP
- Preflights generates artifacts
- Claude resumes implementation

### 8.3 MCP Tools

- `require_clarification` — Clarification and TASK/ADR generation
- `read_architecture` — Read `ARCHITECTURE_STATE.md`

---

## 9. Clarification Loop

### 9.1 Conceptual Flow

```
1. INPUT
   ├── User intention
   ├── Session state (questions/answers)
   └── Filtered and redacted context

2. LLM → STRUCTURED OUTPUT
   ├── questions[] (1..N)
   ├── missing_info[] (semantic keys, 1:1 with questions)
   ├── decision_hint (task | adr | unsure)
   └── progress (0.0 to 1.0)

3. PREFLIGHTS
   ├── Displays questions
   ├── Collects answers
   └── Updates state

4. STOP CONDITION
   └── missing_info empty → deterministic generation
```

### 9.2 Response Types

```python
@dataclass(frozen=True)
class LLMResponse:
    """Structured LLM response."""
    questions: tuple[Question, ...]
    missing_info: tuple[str, ...]  # Semantic keys (1:1 with questions)
    decision_hint: Literal["task", "adr", "unsure"]
    progress: float  # 0.0 to 1.0
```

### 9.3 Field Semantics

| Field | Role | Usage |
|-------|------|-------|
| `questions[]` | User-facing questions | CLI/MCP display |
| `missing_info[]` | Stable semantic keys | Cross-session tracking, progress |
| `decision_hint` | Non-binding indication | Informational only |
| `progress` | Completion estimate | Progress display |

**Critical rule:** `decision_hint` is purely informational. The TASK vs ADR decision is made by the Core deterministically.

---

## 10. LLM Provider & Credentials (BYOK)

### 10.1 Principle

Preflights is **open-source and free**:
- No managed LLM
- No usage billing
- User provides their own credentials (Bring Your Own Key)

### 10.2 Configuration

**Environment variables:**

| Variable | Values | Description |
|----------|--------|-------------|
| `PREFLIGHTS_LLM_PROVIDER` | `mock` \| `anthropic` \| `openai` \| `openrouter` | Provider to use (default: `mock`) |
| `PREFLIGHTS_LLM_MODEL` | string | Specific model (optional) |

**Credentials** (prefixed variables take priority):

| Provider | Variables (by priority order) |
|----------|-------------------------------|
| Anthropic | `PREFLIGHTS_ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY` |
| OpenAI | `PREFLIGHTS_OPENAI_API_KEY`, `OPENAI_API_KEY` |
| OpenRouter | `PREFLIGHTS_OPENROUTER_API_KEY`, `OPENROUTER_API_KEY` |

### 10.3 Security Rules

- Credentials loaded only from local environment
- **Never** stored or logged
- If absent: fallback to `mock` or error if `--llm-strict`

### 10.4 Implementation (Adapter Pattern)

| Adapter | Behavior |
|---------|----------|
| `MockLLMAdapter` | Deterministic (keywords/rules), default and fallback |
| `AnthropicLLMAdapter` | Tool use, model: `claude-sonnet-4-20250514` |
| `OpenAILLMAdapter` | Function calling, model: `gpt-4o` |
| `OpenRouterLLMAdapter` | OpenAI-compatible API |

### 10.5 Structured Output

The LLM must produce **strictly structured** outputs:
- **Anthropic**: Tool use
- **OpenAI / OpenRouter**: Function calling
- Raw JSON = technical fallback only

---

## 11. Context Sent to LLM

### 11.1 Minimization Principle

Preflights **never** transmits the raw workspace.

**Allowed content:**
- User intention
- Session state (questions asked, answers)
- Titles of existing ADRs and TASKs (without content)
- Expected template outlines
- High-level directory summary

**Always excluded:**
- `.env*`, secrets, keys, tokens
- Logs, dumps, exports
- Personal data

### 11.2 Automatic Redaction

Patterns redacted by default:
- API keys (sk-*, AKIA*, etc.)
- JWT tokens
- Emails
- Generic secrets (`password=`, `token=`, etc.)

Any sensitive content → `[REDACTED]`

### 11.3 LLMContext Type

```python
@dataclass(frozen=True)
class LLMContext:
    """Filtered and redacted context for the LLM."""
    file_summary: str  # High-level summary (no raw paths)
    technology_signals: tuple[tuple[str, str], ...]  # (type, value)
    architecture_summary: str | None  # Existing decisions
```

---

## 12. Robustness and Fallback

### 12.1 Parameters

| Parameter | Value |
|-----------|-------|
| Timeout per call | 15 seconds |
| Max retries | 2 |
| Fallback | MockLLMAdapter |

### 12.2 Fallback Behavior

```
LLM Error → Retry (max 2) → Fallback MockLLM + Visible Warning
```

**Rules:**
- Fallback **never silent**: explicit warning displayed
- `--llm-strict` mode: explicit error, no fallback

### 12.3 CLI Flags

| Flag | Behavior |
|------|----------|
| (none) | Mock by default |
| `--llm` | Activates configured provider |
| `--llm-strict` | Fail on LLM error (no fallback) |
| `--llm-provider <name>` | Override provider |

---

## 13. Core Types

### 13.1 Question

```python
@dataclass(frozen=True)
class Question:
    id: str
    type: Literal["single_choice", "multi_choice", "free_text"]
    question: str
    options: tuple[str, ...] | None = None
    optional: bool = False
    depends_on_question_id: str | None = None  # Conditional visibility
    depends_on_value: str | None = None
```

### 13.2 DecisionPatch

```python
@dataclass(frozen=True)
class DecisionPatch:
    """Structured patch for architecture."""
    category: str  # Authentication, Database, Frontend, etc.
    fields: tuple[tuple[str, str], ...]  # (field_key, value)
```

### 13.3 Session

```python
@dataclass
class Session:
    id: str
    repo_path: str
    intention: str
    created_at: float
    expires_at: float  # TTL: 30 minutes

    asked_questions: tuple[Question, ...] = ()
    answers: dict[str, str | tuple[str, ...]] = field(default_factory=dict)

    # LLM tracking
    missing_info: tuple[str, ...] = ()
    decision_hint: str | None = None
    llm_provider_used: str | None = None
    llm_fallback_occurred: bool = False
```

---

## 14. Distribution

### 14.1 Installation

```bash
# Recommended
uvx preflights start "Add authentication"

# Alternatives
pipx install preflights
pip install preflights
```

### 14.2 Optional Dependencies

```bash
# To use Anthropic
pip install preflights[anthropic]

# To use OpenAI/OpenRouter
pip install preflights[openai]

# All providers
pip install preflights[llm]
```

---

## 15. Metrics (MVP)

### 15.1 Hypothesis

Preflights reduces rework by forcing clarification.

### 15.2 Priority Metrics

1. **Iterations per feature** — Target: ≤ 2 (baseline: 3-4)
2. **Time from intention to PR merged** — Target: ≤ 15 min (baseline: 35 min)
3. **Documented decision coverage** — Target: ≥ 80%
4. **Scope violation rate** — Target: ≤ 10%

---

## 16. Fundamental Principles

| Principle | Description |
|-----------|-------------|
| **LLM = Clarification** | The LLM proposes, never decides |
| **Core = Authority** | All final decisions are deterministic |
| **Determinism** | Same inputs → Same outputs |
| **Security** | Never send secrets to the LLM |
| **Resilience** | Fallback visible, never silent |
| **BYOK** | No paid service, user brings their own keys |

---

## 17. Summary

Preflights transforms:

```
Vague intention → Arbitrary implementation → Debt
```

Into:

```
Vague intention → Clarification → Explicit decisions → Aligned implementation
```

It doesn't slow down development.
It prevents making bad decisions too quickly.
