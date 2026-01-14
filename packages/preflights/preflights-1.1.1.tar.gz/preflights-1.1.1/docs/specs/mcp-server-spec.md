# MCP_SPEC_V2.md — Preflights MCP Server Specification

**Product:** Preflights
**Version:** 1.0.0  
**Purpose:** Deterministic clarification and documentation layer (ADR/TASK) for Claude Code via MCP
**Golden Path:** CLI-first (`uvx preflights ...`). MCP is a fallback "catch-up" path.

---

## 1. Scope & Goals

### 1.1 Goals

- Force clarification when a request is ambiguous or structurally impactful
- Generate and maintain repository artifacts:
  - `docs/adr/<UID>_<slug>.md` (immutable)
  - `docs/CURRENT_TASK.md` (mutable)
  - `docs/ARCHITECTURE_STATE.md` (generated projection)
  - `docs/archive/task/<UID>_<slug>.md` (immutable archive)
- Provide a stable MCP contract for Claude Code to:
  - Request clarification (`require_clarification`)
  - Read current architecture (`read_architecture`)

### 1.2 Non-Goals

- No code generation
- No PR / merge lifecycle management
- No ADR status workflow (Git is the lifecycle)
- No IDE-specific UX beyond MCP tool calls
- No ticketing-system integration (Jira, Linear, etc.)

### 1.3 Explicit Exclusions (V2)

**MCP does not generate prompts.**

The `AGENT_PROMPT.md` file is a CLI/UX responsibility only.
MCP is limited to decision artifacts: ADR, TASK, ARCHITECTURE_STATE.

This separation ensures:
- MCP remains a pure decision/documentation layer
- Prompt generation is owned by the presentation layer (CLI)
- Future MCP clients can build their own prompt strategies

---

## 2. Repository Contract (Files & Conventions)

### 2.1 Canonical Paths

```
docs/
├── ARCHITECTURE_STATE.md
├── CURRENT_TASK.md
├── AGENT_PROMPT.md          # CLI-only, not MCP
├── adr/
│   └── <UID>_<slug>.md
└── archive/
    └── task/
        └── <UID>_<slug>.md
```

- `<slug>` is human-readable and decorative
- **UID is the sole identifier**. The slug is never used for references.

### 2.2 UID-Based Ordering & Identity (Normative)

#### UID Format

```
YYYYMMDDTHHMMSS.mmmZ-XXXX
```

Example:
```
20250108T143512.237Z-A001
```

#### Identity Rules

- **ADR identity = UID**
- **TASK identity (archived) = UID**
- There is **no numeric sequence**, no renumbering, no human-maintained counter
- UID is globally unique by construction

#### Ordering Rules

- Canonical order is **lexicographical order of UID**
- "Latest ADR" = ADR with the highest UID
- This ordering is deterministic across branches and machines

#### Branching & Concurrency

- Parallel branches may generate ADRs/tasks independently
- UID guarantees **zero collisions**
- No merge-time renaming or renumbering is required
- Git merge conflicts only occur on content, never on identity

### 2.3 Immutability Rules

- ADR files are immutable once created
- Archived TASK files are immutable
- Any amendment produces:
  - A new ADR (with a new UID), and/or
  - A new CURRENT_TASK.md (previous one archived)

### 2.4 Projection Rule

- `ARCHITECTURE_STATE.md` is **always generated** from the latest ADR
- It contains **PART 1 (snapshot) only**
- It is never a source of truth
- It must be safe to delete and regenerate at any time

---

## 3. Conceptual Model

### 3.1 Session

Clarification is stateful and may require multiple turns.

A session contains:
- `session_id`
- `user_intention`
- `optional_context`
- `questions[]` (visible + conditional)
- `answers` (partial or complete)
- `missing_info[]` (semantic keys from LLM)
- `decision_hint` (informative only)

**MCP sessions are ephemeral per MCP server lifetime.**
No cross-restart guarantee. Sessions are stored in-memory only.
When the MCP server process restarts, all sessions are lost.

### 3.2 Questions

#### Limits

- **Maximum 5 questions per session**
- If more clarification is required → start a new session

#### Question Types

**1. Single Choice**
```json
{
  "id": "auth_strategy",
  "type": "single_choice",
  "question": "Which authentication strategy?",
  "options": ["OAuth", "Email/Password", "Magic Links", "Other (specify)"]
}
```

**2. Multi Choice**
```json
{
  "id": "oauth_providers",
  "type": "multi_choice",
  "question": "Which OAuth providers?",
  "options": ["Google", "GitHub", "Other (specify)"],
  "min_selections": 1
}
```

**3. Free Text**
```json
{
  "id": "security_constraints",
  "type": "free_text",
  "question": "Any specific security requirements?",
  "optional": true
}
```

#### Conditional Questions

MCP clients receive **flat question lists**.
Conditional questions (with `depends_on_question_id`) are:
- Filtered out from MCP responses
- Handled internally by Application layer
- Transparent to MCP clients

### 3.3 ADR Heuristics (V2)

An ADR must be generated if any of the following apply:

**Category-Based Triggers:**
- auth, authentication
- database, storage, cache
- framework, runtime
- deployment, infrastructure
- queue, messaging

**Scope-Based Triggers:**
- Introduces a new dependency (library, service, SaaS)
- Modifies an existing ADR category
- Expected to touch 10+ files
- Requires migration or cross-cutting change

**Explicit User Intent:**
- User mentions "architecture", "strategy", "approach"
- User explicitly asks for an ADR

**Explicit Non-Triggers:**
- Bug fixes
- Pure refactors within existing patterns
- Config-only changes (e.g., adding OAuth provider)

---

## 4. MCP Tools

MCP exposes **2 tools** in V2:
- `require_clarification` — Start/continue clarification, generate artifacts
- `read_architecture` — Read current architecture snapshot

---

### 4.1 Tool: require_clarification

**Intent:** Start or continue clarification and generate ADR/TASK artifacts.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_intention": { "type": "string" },
    "optional_context": { "type": "string", "nullable": true },
    "session_id": { "type": "string", "nullable": true },
    "answers": {
      "type": "object",
      "additionalProperties": true,
      "nullable": true
    },
    "preferences": {
      "type": "object",
      "properties": {
        "force_adr": { "type": "boolean" }
      },
      "nullable": true
    },
    "repo_path": { "type": "string", "nullable": true }
  },
  "required": ["user_intention"]
}
```

#### Output Schema

**Case A — Needs Clarification**

```json
{
  "status": "needs_clarification",
  "session_id": "sess-abc",
  "questions": [
    {
      "id": "auth_strategy",
      "type": "single_choice",
      "question": "Which authentication strategy?",
      "options": ["OAuth", "Email/Password", "Other (specify)"]
    }
  ],
  "progress": {
    "asked_so_far": 2,
    "answered": 1
  }
}
```

**Case B — Completed**

```json
{
  "status": "completed",
  "artifacts_created": [
    {
      "path": "docs/adr/20250108T143512.237Z-A001_authentication.md",
      "type": "adr",
      "uid": "20250108T143512.237Z-A001"
    },
    {
      "path": "docs/CURRENT_TASK.md",
      "type": "task"
    },
    {
      "path": "docs/ARCHITECTURE_STATE.md",
      "type": "projection"
    }
  ],
  "summary": "OAuth authentication strategy documented and task created."
}
```

**Case C — Error**

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "ADR snapshot validation failed",
    "details": { "missing_keys": ["Database"] },
    "recovery_hint": "Review previous ADR and retry"
  }
}
```

---

### 4.2 Tool: read_architecture

**Intent:** Read current architecture snapshot.

#### Input

```json
{
  "repo_path": "/path/to/repo"  // Optional, auto-discovers from .git
}
```

#### Output

```json
{
  "status": "success",
  "architecture": {
    "uid": "20250108T143512.237Z-A001",
    "categories": {
      "Authentication": {
        "Strategy": "OAuth",
        "Library": "next-auth"
      },
      "Database": {
        "Type": "PostgreSQL",
        "ORM": "Prisma"
      }
    }
  },
  "source_file": "docs/ARCHITECTURE_STATE.md"
}
```

**No ADR exists:**
```json
{
  "status": "success",
  "architecture": {
    "uid": null,
    "categories": {}
  },
  "source_file": "docs/ARCHITECTURE_STATE.md"
}
```

---

## 5. Error Handling

### 5.1 Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `VALIDATION_FAILED` | ADR snapshot invalid | Fix previous ADR |
| `SESSION_EXPIRED` | Session timeout (30 min) | Restart clarification |
| `SESSION_NOT_FOUND` | Unknown session_id | Start new session |
| `FILESYSTEM_ERROR` | Cannot write files | Check permissions |
| `PARSE_ERROR` | Existing file malformed | Manual fix required |
| `REPO_NOT_FOUND` | Repository path invalid | Check repo_path |
| `PATCH_EXTRACTION_FAILED` | LLM extraction failed | Retry |

### 5.2 Error Envelope

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {},
    "recovery_hint": "Next step"
  }
}
```

### 5.3 Session Expiry

- Sessions expire after **30 minutes** of inactivity
- No persistence in V2
- **Sessions are lost on MCP server restart**

---

## 6. Repository Discovery

When `repo_path` is not provided:

1. Start from current working directory
2. Walk up parent directories
3. Find first directory containing `.git/`
4. Use that as repo root

If no `.git/` found:
```json
{
  "status": "error",
  "error": {
    "code": "REPO_NOT_FOUND",
    "message": "No git repository found",
    "recovery_hint": "Run from a git repository or provide repo_path"
  }
}
```

---

## 7. End-to-End Examples

### 7.1 Simple Task (No ADR)

```
User: "Fix typo in login button"
→ One-step clarification
→ CURRENT_TASK.md only
```

### 7.2 Multi-Turn with ADR

```
Turn 1:
  User: "Add authentication"
  → status: needs_clarification
  → questions: [auth_strategy, auth_library]

Turn 2:
  User: answers = {auth_strategy: "OAuth", auth_library: "next-auth"}
  → status: completed
  → artifacts: [ADR, TASK, ARCHITECTURE_STATE]
```

### 7.3 Architecture Query

```
Tool: read_architecture
→ Returns current categories and decisions
→ Agent uses context for implementation
```

---

## 8. LLM Integration (V2)

### 8.1 Provider Configuration

MCP server uses the same LLM configuration as CLI:
- Environment variables: `PREFLIGHTS_LLM_PROVIDER`, etc.
- Default: Mock LLM (deterministic)

### 8.2 Fallback Behavior

If real LLM fails:
- Retry up to 2 times
- Fallback to MockLLM with warning
- Continue clarification (not failure)

Warning included in response:
```json
{
  "warning": "llm_fallback",
  "message": "LLM unavailable, using deterministic mode"
}
```

---

## 9. Summary

| Aspect | Specification |
|--------|--------------|
| Identity | UID-first everywhere |
| Ordering | Lexicographical UID order |
| Conflicts | Zero by design |
| IDs | No dual IDs (human vs machine) |
| Branching | Deterministic, branch-safe, Git-native |
| Golden Path | CLI-first, MCP is fallback |
| Tools | 2 tools only |
| Prompts | CLI responsibility, not MCP |
| Sessions | Ephemeral per server lifetime |
| LLM | Configurable, with fallback |
