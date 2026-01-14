# GOLDEN_PATH_V2.md — Preflights Golden Path

**Product:** Preflights
**Version:** 1.0.0  
**Philosophy:** Code Less, Specify More.
**Goal:** Let developers "vibe code" fast without sacrificing architectural clarity.

---

## 1. Target Audience

Preflights V2 targets developers using coding agents (Claude Code, Cursor, Windsurf) who want:
- Fast implementation
- Zero ambiguity on decisions and scope
- Explicit architectural decisions documented

Preflights is not a code generator. It produces artifacts that make agents implement without "deciding in the dark".

---

## 2. The Canonical User Journey

The user flow is intentionally linear:

```
1. Human provides intention          "Add OAuth authentication"
         ↓
2. Preflights asks clarification     Which strategy? Which library?
         ↓
3. Human answers questions           OAuth, next-auth
         ↓
4. Preflights generates artifacts    TASK + ADR + ARCHITECTURE_STATE + AGENT_PROMPT
         ↓
5. Coding agent implements           Reads AGENT_PROMPT.md, implements scope
```

Preflights is the "decision & specification gate" before implementation.

---

## 3. The Single Command

The Golden Path is one interactive command, run from anywhere inside the repository:

```bash
pf start "<intention>" [options]
```

### 3.1 Options

| Option | Description |
|--------|-------------|
| `--repo-path PATH` | Override repository path (auto-discovers via `.git`) |
| `--non-interactive` | Show questions and exit (for scripts/CI) |
| `--json` | Machine-readable output (implies `--non-interactive`) |
| `--llm` | Enable real LLM provider |
| `--llm-strict` | Fail on LLM errors (no fallback to mock) |
| `--llm-provider NAME` | Override provider: `anthropic`, `openai`, `openrouter` |

### 3.2 Defaults

- **Interactive mode** by default
- **Repo root auto-discovered** by walking up to find `.git`
- **Session stored locally** under `<repo_root>/.preflights/`
- **Mock LLM** unless `--llm` or `--llm-provider` specified

### 3.3 Non-Goal

The "start + stop + answer later" workflow is **not** the Golden Path.
It exists for scripts and CI but is not the flagship experience.

---

## 4. Interactive Loop (Core of the Golden Path)

In interactive mode, `pf start` runs a loop until completion or error:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Start PreflightsApp session (start_preflight)           │
│ 2. Display questions                                        │
│ 3. Collect user answers (inline, with validation)          │
│ 4. Continue session (continue_preflight)                    │
│ 5. Handle result:                                           │
│    ├── needs_more_answers → loop (remaining questions)      │
│    ├── needs_clarification → loop (follow-up questions)     │
│    ├── completed → write artifacts, display prompt, exit 0  │
│    └── error → show recovery hint, exit non-zero            │
└─────────────────────────────────────────────────────────────┘
```

The CLI **never requires a second command** in the normal flow.

---

## 5. Question UX Rules

### 5.1 Question Types

| Type | Description | Example |
|------|-------------|---------|
| `single_choice` | Select one option | "Which strategy?" |
| `multi_choice` | Select one or more | "Which providers?" |
| `free_text` | Free input | "Describe constraints" |

### 5.2 "Other (Specify)" Pattern

For every `single_choice` and `multi_choice` question, the UI always offers:
- The provided options
- Plus an extra option: **"Other (specify)"**

When selected:
1. A text input appears immediately
2. User types freely
3. Input is mapped internally to a hidden `__other` question

**UX Requirement:** For the user it feels like **one** question, not two.

### 5.3 Internal Model

```
Visible question:     auth_strategy (single_choice)
Hidden question:      auth_strategy__other (free_text, optional)
                      depends_on_question_id = "auth_strategy"
                      depends_on_value = "Other (specify)"
```

The hidden question is:
- Only shown if parent value = "Other (specify)"
- Filtered out in MCP (Application handles visibility)
- Transparent to Core (receives normalized answers)

---

## 6. Session Management

### 6.1 Session Storage

```
<repo_root>/
├── .preflights/
│   ├── session.json         # Active session state
│   └── last_intention.txt   # For resume after interruption
└── .gitignore               # Auto-includes .preflights/
```

### 6.2 Session Lifecycle

| State | Duration | Behavior |
|-------|----------|----------|
| Active | TTL: 30 minutes | Questions + answers stored |
| Expired | After TTL | Session cleared, user must restart |
| Completed | After artifacts written | Session deleted |
| Error | On failure | Session preserved for resume |

### 6.3 Session Rules

- `.preflights/` is git-ignored (auto-added to `.gitignore` if missing)
- `docs/` artifacts are committed
- On completion, `session.json` is removed
- On error, `session.json` is preserved to allow resume

---

## 7. Outputs (What Preflights Produces)

### 7.1 Artifacts

| File | Description | Mutability |
|------|-------------|------------|
| `docs/CURRENT_TASK.md` | Active implementation brief | Mutable (replaced per run) |
| `docs/adr/<UID>_<slug>.md` | Architectural decision record | Immutable |
| `docs/ARCHITECTURE_STATE.md` | Current architecture snapshot | Generated projection |
| `docs/AGENT_PROMPT.md` | Copy-paste prompt for coding agent | Generated |
| `docs/archive/task/` | Archived previous tasks | Immutable |

### 7.2 Artifact Rules

- ADR files are **immutable** once created
- `ARCHITECTURE_STATE.md` is a **generated projection** (never source of truth)
- `CURRENT_TASK.md` is the only active task file; previous one is archived
- `AGENT_PROMPT.md` contains the formatted prompt to give to the coding agent

---

## 8. What the Coding Agent Does Next

After completion:

1. Human opens their coding agent (Claude Code, Cursor, Windsurf)
2. Human copy-pastes the content of `docs/AGENT_PROMPT.md` (or reads it directly)
3. Agent reads:
   - `docs/CURRENT_TASK.md` (implementation brief)
   - `docs/ARCHITECTURE_STATE.md` (technical context)
4. Agent implements **without introducing new decisions outside the task scope**

If the agent hits ambiguity or a new decision is required:
- The correct move is to run another Preflight (new task and possibly new ADR)

---

## 9. LLM Configuration

### 9.1 BYOK (Bring Your Own Key)

Preflights is **open-source and free**:
- No managed LLM
- No usage billing
- Users provide their own API keys

### 9.2 Provider Configuration

```bash
# Default: Mock LLM (deterministic, no API calls)
pf start "Add authentication"

# Enable real LLM (with fallback to mock on error)
pf start "Add authentication" --llm

# Strict mode (fail on LLM error, no fallback)
pf start "Add authentication" --llm --llm-strict

# Specific provider
pf start "Add authentication" --llm-provider anthropic
```

### 9.3 Environment Variables

| Variable | Description |
|----------|-------------|
| `PREFLIGHTS_LLM_PROVIDER` | Default provider: `mock`, `anthropic`, `openai`, `openrouter` |
| `PREFLIGHTS_ANTHROPIC_API_KEY` | Anthropic API key (priority over `ANTHROPIC_API_KEY`) |
| `PREFLIGHTS_OPENAI_API_KEY` | OpenAI API key |
| `PREFLIGHTS_OPENROUTER_API_KEY` | OpenRouter API key |

### 9.4 Fallback Behavior

```
LLM Error → Retry (max 2) → Fallback to MockLLM + Warning visible
```

- Fallback is **never silent** (warning displayed)
- `--llm-strict` disables fallback (error on failure)

---

## 10. Failure & Recovery

### 10.1 Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `NOT_A_REPOSITORY` | No `.git` found | Run from a git repository |
| `SESSION_EXPIRED` | Session timed out | Use `pf resume` |
| `FILESYSTEM_ERROR` | Cannot write docs/ | Check permissions |
| `PATCH_EXTRACTION_FAILED` | LLM extraction failed | Retry or use `--llm` |
| `LLM_CREDENTIALS_MISSING` | API key not found | Set environment variable |

### 10.2 Recovery Commands

```bash
pf resume                # Restart with last intention
pf status                # Inspect local session
pf reset                 # Cancel local session
```

These are **not part of the normal Golden Path** — most users never need them.

---

## 11. Non-Interactive Mode

Non-interactive is supported for CI/scripts only:

```bash
pf start "<intention>" --non-interactive --json
pf answer key=value key2=value2 --json
```

But the flagship experience of V2 is interactive "one command" usage.

---

## 12. Definition of Done

The Golden Path is complete when a user can:

1. Run `pf start "<intention>"`
2. Answer all questions in the same run
3. Complete the session without copying IDs or editing files manually
4. End with `docs/CURRENT_TASK.md` written (and ADR/STATE if applicable)
5. See `docs/AGENT_PROMPT.md` content displayed for copy-paste
6. Hand off to a coding agent that can implement without guessing architecture
