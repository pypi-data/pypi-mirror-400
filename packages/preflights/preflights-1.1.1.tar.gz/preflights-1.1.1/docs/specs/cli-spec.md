# Preflights CLI — Interactive Mode V2 (Normative Spec)

**Product:** Preflights
**CLI name:** `pf`
**Version:** 1.0.0  
**Audience:** Human developers (Golden Path), scripts/CI in fallback
**Goal:** Make `pf start "<intention>"` fluid, one command, without breaking automation

---

## 1. Fundamental Principle

By default, the CLI is **interactive**.

```bash
pf start "Add authentication"
```

This single command:
1. Starts a session
2. Asks questions
3. Collects answers
4. Generates artifacts
5. Displays agent prompt
6. Terminates

**One command for a human.**

Non-interactive mode remains available explicitly for scripts.

---

## 2. Commands and Modes

### 2.1 Main Command

```bash
pf start "<intention>" [--repo-path PATH] [--non-interactive] [--json]
                        [--llm] [--llm-strict] [--llm-provider NAME]
```

### 2.2 Mode Selection Rules

| Flags | Mode |
|-------|------|
| (none) | Interactive (default) |
| `--non-interactive` | Display questions and exit |
| `--json` | Machine-readable output, non-interactive |

### 2.3 LLM Configuration

| Flag | Behavior |
|------|----------|
| (none) | Mock LLM (deterministic) |
| `--llm` | Enable real LLM from environment |
| `--llm-strict` | Fail on LLM error (no fallback) |
| `--llm-provider NAME` | Override provider, implies `--llm` |

Interactive mode and non-interactive mode share **strictly the same backend** (PreflightsApp).

---

## 3. Global Interactive Flow (Golden Path)

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. Discover repository (or use --repo-path)                      │
│ 2. Call start_preflight(intention, repo_path)                    │
│ 3. Store session locally (.preflights/session.json)              │
│ 4. Configure LLM if --llm or --llm-provider specified            │
│ 5. Enter interactive loop:                                       │
│    ├── Display questions (filtered, no conditional)              │
│    ├── Prompt for answers (with validation)                      │
│    ├── Call continue_preflight(session_id, answers_delta)        │
│    └── Handle result:                                            │
│        ├── needs_more_answers → loop (remaining questions)       │
│        ├── needs_clarification → loop (follow-up questions)      │
│        ├── completed → display artifacts + agent prompt, exit 0  │
│        └── error → display error + recovery hint, exit non-zero  │
└──────────────────────────────────────────────────────────────────┘
```

The program **never stops** while status is not `completed` or `error`.

---

## 4. Question Display Rules

Each question is displayed as:

```
Q[n] [question_id]: Question text
   Type: single_choice | multi_choice | free_text
   Options: option1, option2, ... (if applicable)
   Min: N, Max: M (if multi_choice with constraints)
   (optional) (if question is optional)
```

**Conditional questions** (with `depends_on_question_id`) are **hidden** until their parent condition is met.

---

## 5. Input by Question Type

### 5.1 free_text

- User enters a line freely
- If empty:
  - `optional=false` → re-prompt
  - `optional=true` → skip

### 5.2 single_choice

- Options are numbered: `1. OAuth  2. Email/Password  3. Other (specify)`
- User can respond by:
  - Number: `1`, `2`, `3`
  - Exact text (case-insensitive): `oauth`, `OAuth`

**Strict validation:**
- Exactly one option
- Must be a valid option

### 5.3 multi_choice

- Options are numbered
- User can respond by:
  - Comma-separated numbers: `1,2`
  - Comma-separated texts: `Google, GitHub`

**Strict validation:**
- Respects `min_selections` and `max_selections`
- All values must be valid options

---

## 6. "Other (specify)" Rule (MANDATORY)

All `single_choice` and `multi_choice` questions **systematically** include:

```
Other (specify)
```

This is a **product rule**, not optional.

### 6.1 User Experience

For the user, it's a **single fluid question**:

```
Which authentication strategy do you want to use?
  1. OAuth
  2. Email/Password
  3. Magic Link
  4. Other (specify): ________
```

Behavior:
- While "Other" is not selected → text field hidden
- When "Other" is selected → immediate free input
- No notion of "additional question" visible

### 6.2 System Model

Behind the scenes, the system manipulates **two distinct questions**:

**Visible question:**
```python
Question(
    id="auth_strategy",
    type="single_choice",
    options=("OAuth", "Email/Password", "Magic Link", "Other (specify)")
)
```

**Associated logical question:**
```python
Question(
    id="auth_strategy__other",
    type="free_text",
    optional=True,
    depends_on_question_id="auth_strategy",
    depends_on_value="Other (specify)"
)
```

**Mapping sent to continue_preflight:**
```python
{
    "auth_strategy": "Other (specify)",
    "auth_strategy__other": "Custom SAML provider"
}
```

---

## 7. Responsibilities by Layer

### 7.1 Core

- **No change**
- Does not know "Other"
- Receives only normalized answers

### 7.2 Application / LLMAdapter

- Automatically adds "Other (specify)" option
- Generates associated `__other` question
- Applies conditional logic
- Normalizes answers before calling Core

### 7.3 CLI

- Manages conditional display
- Ensures fluid UX
- Batches answers before calling continue_preflight

---

## 8. Answer Batching (Important)

In interactive mode, the CLI **MUST**:
- Collect multiple answers locally
- Send a single `answers_delta` per logical cycle

**Goals:**
- Reduce API calls
- Avoid choppy UX
- Remain compatible with public contract

---

## 9. Status Handling

### 9.1 needs_more_answers

- Display only unanswered questions
- Continue loop

### 9.2 needs_clarification

- Display new follow-up questions from Core
- Continue loop

### 9.3 completed

Display:
- Path to `CURRENT_TASK.md`
- Path to ADR (if created)
- Path to `ARCHITECTURE_STATE.md` (if updated)
- Path to `AGENT_PROMPT.md`
- **Agent prompt content** (for copy-paste)

Then:
- Delete local session
- Exit 0

### 9.4 error

- Display error code + message + recovery hint
- Preserve local session for resume
- Exit non-zero

---

## 10. LLM Fallback Warning

When the real LLM fails and falls back to mock:

```
⚠ Warning: LLM unavailable (timeout), using deterministic mode
```

This warning is:
- Always displayed (never silent)
- Printed to stderr (not stdout)
- Included in JSON output as `warning` field

---

## 11. Other Commands

### 11.1 pf answer

```bash
pf answer key=value key2=value2 [--json] [-i/--interactive]
pf answer --answers-json '{"key": "value"}'
pf answer --answers-file answers.json
```

- Provides answers to existing session
- `-i` continues interactively after providing answers

### 11.2 pf status

```bash
pf status [--json]
```

Displays:
- Current intention
- Session expiration time
- Answered vs pending questions

### 11.3 pf resume

```bash
pf resume [--llm] [--llm-strict] [--llm-provider NAME]
```

- Loads last intention from `.preflights/last_intention.txt`
- Restarts preflight with same intention

### 11.4 pf reset

```bash
pf reset [--force]
```

- Cancels current session
- Clears session file
- Confirms deletion unless `--force`

---

## 12. Why This Design

| Reason | Explanation |
|--------|-------------|
| Interactive = real usage | Humans use interactive mode |
| Non-interactive = CI/scripts | Perfect for automation |
| Core remains pure | No UX knowledge in domain |
| Architecture supports all interfaces | CLI, MCP, future UI |
| Avoids "two commands per intention" | Fluid experience |

---

## 13. Executive Summary

- `pf start` is **interactive by default**
- **One command** for one intention
- "Other (specify)" is **systematic and fluid**
- Core remains **blind to UX**
- Public contract is **unchanged**
- Spec is **V2-compatible and extensible**
- LLM fallback is **visible, never silent**
