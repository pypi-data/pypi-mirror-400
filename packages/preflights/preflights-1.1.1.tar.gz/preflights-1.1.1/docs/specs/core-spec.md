# CORE_SPEC.md — Preflights Core Specification

**Product:** Preflights  
**Version:** 1.0.0  
**Purpose:** Define the platform-agnostic core logic (clarification, ADR detection, artifact construction).  
**Scope:** Pure business logic. No I/O, no UI, no transport (MCP/CLI are adapters).  
**Key rule:** UID-first identity everywhere (UID is the only identifier).

---

## 1. Scope & Principles

### 1.1 Core Responsibilities
The Core is responsible for:
1. **Clarification logic** — propose questions to resolve ambiguity
2. **Decision detection** — decide whether an ADR is required (V1 heuristics)
3. **Artifact construction** — build ADR + Task + updated ArchitectureState (as data structures)
4. **Validation** — enforce invariants (snapshot completeness, task validity, referential integrity)

### 1.2 Core Non-Responsibilities (Adapters)
The Core does NOT:
- Read/write files (Filesystem Adapter)
- Call LLMs (LLM Adapter)
- Handle user I/O (UI Adapter: CLI/MCP)
- Manage sessions or persistence (Session Adapter)
- Manage Git/PR lifecycle (Git is the lifecycle)

### 1.3 Design Principles

- **No I/O, but Context-In**: the Core never reads the filesystem, but it requires a file topology summary as input.
- **Stateless Engine, Stateful Inputs**: the Core keeps no internal state, but it accepts conversation state (asked questions + given answers) as input.
- **Deterministic Given Inputs**: same inputs (including UIDs, timestamps, file_context, conversation_state, config) → same outputs.
- **Schema-guided & Normalized**: snapshots follow a fixed schema; unknown keys are rejected or normalized.
- **Testable**: pure data in/out, no side-effects.
---

## 2. Domain Model (Data Structures)

> Types below describe the **shape**. Implementation language is Python, but the Core must stay adapter-independent.

### 2.0 Fixed Snapshot Schema (V1)

Architecture snapshots are not a free-form map.
They MUST conform to a fixed schema to avoid “format drift” and noisy diffs.

#### 2.0.1 Schema
The snapshot schema is a set of categories and fields, for example:

- Frontend: Framework, Routing, Styling, UI_Library, State_Management
- Backend: Language, Framework, API_Style, Validation
- Database: Type, ORM, Migrations
- Authentication: Strategy, Library, Token_Storage
- Infra: Hosting, CI_CD, Observability, Caching

#### 2.0.2 Normalization Rules (V1)
- Category names are normalized to schema category keys (case-insensitive matching).
- Field names are normalized to schema field keys (case-insensitive matching).
- Unknown categories/fields:
  - **Default policy (V1): REJECT** with `VALIDATION_FAILED` + details.
  - Optional future policy: allow “Other” bucket (V2+).

This guarantees stable snapshots and avoids “scintillating” ARCHITECTURE_STATE.

### 2.1 Intention
- `text` (string)
- `optional_context` (string | null)

### 2.2 Question
- `id` (string, stable)
- `type` (`single_choice` | `multi_choice` | `free_text`)
- `question` (string)
- `options` (string[] | null)
- `min_selections` (int | null)
- `max_selections` (int | null)
- `optional` (bool, default false)

**Constraints (V1):**
- Max **5 questions** per run
- Questions are **independent** (no conditional chains in V1)

### 2.2bis FileContext (Project Topology Summary)

The Core requires a compact view of the repository topology to generate a non-hallucinated allowlist.

- `paths` (string[]) — relevant file paths (or globs) observed in repo
- `high_level_dirs` (string[]) — optional, for routing questions
- `signals` (object) — optional detected signals (e.g., "uses_nextjs": true)

The adapter is responsible for building this summary.
The Core only consumes it.


### 2.3 Answers
- `answers` is a map: `question_id -> value`
- value is `string` or `string[]` depending on question type

### 2.3bis ConversationState (Stateful Input)

The Core is stateless internally, but it must receive the conversation context as input to avoid incoherent follow-up questions.

- `asked_questions` (Question[]) — the exact questions previously asked (IDs + types + options)
- `answers` (map) — current answers
- `turn` (int) — optional, number of clarification turns so far *(not implemented in V1)*
 
**Interpretation rule (MUST):**
- `asked_questions` is authoritative for interpreting `answers`.
- An answer MUST NOT be interpreted without its corresponding Question (id + type + options).

### 2.4 ArchitectureState (Snapshot)

- `uid` (string | null) — UID of the ADR this snapshot comes from (null if none exists)
- `schema_version` (string) — fixed schema version (e.g., "v1")
- `categories` (map constrained by schema):
  - `CategoryKey -> { FieldKey -> ValueString }`

**ValueString convention (UID-first references):**
- Example: `Library: "next-auth (ADR 20250104T143512.237Z)"`
### 2.5 ADR (Decision Record)
- `uid` (string) — injected (UID-first)
- `title` (string)
- `category` (string)
- `date_utc` (string) — injected (UTC)
- `previous_uid` (string | null)

**PART 1: Snapshot**
- `snapshot` (ArchitectureState)
- `changes_in_this_version` (string[]) — explicit list of changes

**PART 2: Decision Details**
- `context` (string)
- `decision` (string)
- `rationale` (string)
- `alternatives` (list)
- `consequences` (positive/negative/neutral lists)
- `supersedes_uid` (string | null)

### 2.6 Task (Execution Brief)
- `uid` (string) — injected (used for archiving CURRENT_TASK)
- `title` (string)
- `objective` (string)
- `context` (string) — references relevant ADRs by UID
- `allowlist` (string[])
- `forbidden` (string[])
- `technical_constraints` (string[])
- `acceptance_criteria` (string[])
- `created_at_utc` (string) — injected (UTC)
- `related_adr_uid` (string | null)

---

## 3. Core Components (Interfaces)
### 3.0 DecisionPatch (required input for deterministic snapshot updates)

To keep snapshot updates deterministic, the Core operates on a structured patch:

- `DecisionPatch`
  - `category` (CategoryKey)
  - `fields` (map FieldKey -> ValueString)
  - `references` (optional: map FieldKey -> UID reference strings)

Rule:
- SnapshotBuilder MUST ONLY apply a DecisionPatch (no free-text parsing inside SnapshotBuilder).

Note (V1):
- DecisionPatch is produced outside SnapshotBuilder (typically by an LLM adapter) and MUST already be schema-normalized.
- Core validation rejects unknown categories/fields before snapshot application.

### 3.1 Clarifier

Responsibility: propose questions to resolve ambiguity.

Inputs:
- Intention
- Current ArchitectureState (optional)
- FileContext (required for accurate scoping)
- ConversationState (asked_questions + answers) to ensure coherent follow-ups

Output:
- questions[] (max 5), independent (no conditional chains in V1)

Rules:
- Never ask a question that was already asked (same question.id) unless explicitly requested by caller.
- Prefer choice questions over free-text.
- Questions must be grounded in schema + file_context (e.g., Next.js detected → ask NextAuth vs Clerk).


### 3.2 DecisionDetector
**Responsibility:** decide if ADR is required (V1 heuristics aligned with MCP_SPEC 3.3).

Input:
- Intention
- Answers
- Optional metadata (estimated_file_impact, new_dependencies, detected_keywords)

Output: ADRDecision
- `needs_adr` (bool)
- `category` (string | null)
- `triggered_by` (string[])
- `rationale` (string)

### 3.3 SnapshotBuilder
**Responsibility:** build snapshots deterministically by applying a structured DecisionPatch.

Inputs:
- Previous snapshot (ArchitectureState | null)
- `decision_patch` (DecisionPatch)  ← REQUIRED
- Injected `new_adr_uid` (string)

Output:
- New ArchitectureState

Rules:
- Preserve all categories/fields by default
- Only mutate the target category/fields described by `decision_patch`
- Never “drop” keys silently
- No free-text parsing is allowed inside SnapshotBuilder


### 3.4 ADRBuilder
**Responsibility:** build a complete ADR data structure from:
- decision outcome (category, fields)
- new snapshot
- injected UID + date + previous_uid
- injected “changes_in_this_version” list

### 3.5 TaskBuilder
**Responsibility:** build a Task data structure.

Key requirements:
- Allowlist must be non-empty
- Forbidden must not overlap allowlist
- Acceptance criteria must be observable/testable (>= 1)

#### Allowlist validity (MUST)

- The generated allowlist MUST be grounded in `file_context.paths`.
- Each allowlist entry MUST be either:
  1) an exact path present in `file_context.paths`, OR
  2) a glob that matches at least 1 path in `file_context.paths`.
- Globs that match "too broad" patterns (e.g., "**/*") SHOULD be rejected in V1.

---

## 4. Orchestration (Core Entry Point)

### 4.1 PreflightsCore.process()

Stateless entry point.

Inputs:
- intention
- current_architecture (ArchitectureState | null)
- file_context (FileContext)  ← REQUIRED
- conversation_state (ConversationState | null)
- metadata (optional: estimated_file_impact, new_dependencies, keywords_detected)
- injected values:
  - uid_for_adr (string | null)
  - uid_for_task (string | null)
  - now_utc (string | null)
- heuristics_config (HeuristicsConfig) ← REQUIRED (see section 6)

Rules:
- If outputs require creating artifacts (ADR/TASK), then uid_for_task + now_utc MUST be provided.
- If ADR is created, uid_for_adr MUST be provided.
- If not enough information exists to produce a grounded allowlist or stable snapshot update, the Core MUST return `needs_clarification`.

Output: one of two shapes:

#### Case A — Needs user input
- `status: "needs_clarification"`
- `questions[]`

#### Case B — Completed (artifacts ready)
- `status: "completed"`
- `task` (Task)
- `adr` (ADR | null)
- `updated_architecture` (ArchitectureState | null)
    - If ADR created: snapshot uid = `uid_for_adr`
    - If no ADR: unchanged current_architecture

**Important:**
- The Core does not allocate UIDs. It consumes injected UIDs.
- The adapter decides when to call again (session loop is outside Core).

#### Case C — Error
- `status: "error"`
- `error: { code, message, details, recovery_hint }`

Error codes should mirror MCP_SPEC where possible (e.g., `VALIDATION_FAILED`, `PARSE_ERROR` for malformed inputs, etc.).

---

## 5. Validation Rules (Invariants)

### 5.1 Snapshot Validation (MUST)
- All categories present in previous snapshot must still exist **unless explicitly removed** in `changes_in_this_version`.
- All category/field names must be stable (no accidental renames).
- All ADR references must be UID-based (pattern check).

On failure: return `status: "error"` with `VALIDATION_FAILED`.

### 5.2 Task Validation (MUST)
- Allowlist: >= 1 entry
- Forbidden: optional, but must not overlap allowlist
- Acceptance criteria: >= 1, each must be “testable/observable”
    - Examples:
        - ✅ “Login with Google works and redirects to /dashboard”
        - ✅ “Tokens are stored in httpOnly cookies”
        - ❌ “Auth is good”

### 5.3 ADR Validation (MUST when ADR exists)
- UID format valid: `YYYYMMDDTHHMMSS.mmmZ`
- Snapshot passes validation
- Decision details minimal quality gates:
    - Context/Decision/Rationale not empty
    - Alternatives list has at least 1 entry (can be “None considered” with rationale)

### 5.4 State Corruption & Rebase (MUST)

If current_architecture (or parsed snapshot) is malformed or violates schema:
- Return `status: "error"` with code `STATE_CORRUPTION`
- Include details about the first invalid category/field encountered
- Provide recovery_hint:
  - "Fix/restore latest ADR snapshot" OR
  - "Run preflights rebase (adapter feature) to regenerate a clean snapshot from the repository baseline"

The Core does not perform the rebase automatically; it only signals the condition.

---

## 6. Heuristics (V1)

### 6.0 HeuristicsConfig (Injected)

The Core must not hardcode ecosystem keywords (next-auth, clerk, etc.).
All heuristics data is injected.

HeuristicsConfig contains:
- category_keywords: map Category -> string[]
- question_templates: map Category -> QuestionTemplate[]
- non_triggers: string[] (e.g., "bugfix", "typo")
- adr_triggers:
  - file_impact_threshold (default 10)
  - dependency_trigger (bool)
- schema: the fixed snapshot schema definition (see 2.0)
- keyword_to_category: map string -> CategoryKey (used to select the ADR category deterministically)

### 6.1 Question Generation Heuristics (examples)
- If intention contains `auth/login`:
    - strategy (uses config.category_keywords[…])
    - library (uses config.category_keywords[…])
    - providers (if OAuth)
- If intention contains `database`:
    - DB type, ORM, migration tool
- If intention contains `cache`:
    - cache type, TTL strategy

**Rule:** stop at 5 questions maximum.

### 6.2 ADR Detection Heuristics (aligned with MCP_SPEC)
ADR if ANY:
- category keywords hit (auth/database/framework/deploy/cache/queue)
- introduces new dependency/service
- modifies an existing ADR category
- expected >= 10 files impacted
- user explicitly asks for strategy/architecture

No ADR if:
- bug fix
- refactor within existing pattern
- config-only change

---

## 7. Required Adapter Contracts (to keep Core deterministic)

To keep the Core deterministic, adapters must provide:

### 7.1 UID Provider
- Generates UID string in required format (UTC + ms)
- Used for ADR uid and Task archive uid

### 7.2 Clock Provider
- Provides `now_utc` as string (UTC)

### 7.3 Optional Metadata Provider (future)
- estimated_file_impact
- new_dependencies
- keywords_detected

(V1 can set these to defaults if not available.)

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Clarifier: never >5 questions; stable IDs
- SnapshotBuilder: preserves all non-target keys; never drops categories
- Validators: catch overlaps, empty allowlist, missing acceptance criteria

### 8.2 Integration Tests
Given:
- current_architecture snapshot
- intention + answers
- injected uid(s) + now_utc
  Expect:
- deep-equal outputs for same inputs
- ADR created only when heuristics trigger
- updated_architecture consistent with ADR snapshot

---

## 9. Summary

- The Core is pure logic: clarify → detect ADR → build artifacts → validate.
- The Core is stateless and deterministic (UID/time injected).
- UID-first identity everywhere; no numeric ordering in Core.
- Adapters (CLI/MCP/FS/LLM) wrap the Core without contaminating business logic.