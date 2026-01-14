# Preflights

Code fast with AI — without giving up architectural clarity.

Preflights is a lightweight CLI tool that helps developers clarify decisions before letting an AI agent write code.
It turns a vague intention into explicit decisions and a clear execution brief — without slowing you down.

---

## What is Preflights?

Preflights sits before AI coding agents (Claude Code, Cursor, Windsurf).

It does not generate code.
It forces clarification, captures architectural decisions, and produces a clear execution brief so AI agents can implement without guessing or redefining scope.

Think of it as a pre-flight checklist for AI-assisted development.

---

## How Preflights uses AI (and how it doesn't)

Preflights may optionally use an LLM **only** to generate clarification questions and progress signals.

It never:
- generates code
- makes architectural decisions
- writes files directly
- replaces deterministic logic

All decisions, validations, and artifacts are produced by a deterministic core.
The LLM is treated as an interchangeable clarification engine — not an authority.

The deterministic MockLLMAdapter defines the reference behavior.
LLM-backed modes must align with it.

---

## Why Preflights exists

AI coding tools are incredibly fast.
The real problem is not speed — it's everything that gets decided implicitly:

- architectural choices made by accident
- inconsistencies across files
- rework disguised as "fast iteration"
- technical debt with no paper trail

With vibe coding, you often have to choose:

- move fast
- or keep quality and clarity

Preflights removes that trade-off.

You can keep the vibe — while making decisions explicit, traceable, and reversible.

---

## Quickstart

From the root of a git repository:

```bash
pf start "Add user authentication"
```

Or with uvx (no install needed):

```bash
uvx preflights start "Add user authentication"
```

Preflights will:

- ask a few targeted clarification questions
- distinguish decisions from implementation details
- generate clear artifacts for your AI agent

That's it.

Preflights is fully open-source and does not provide or manage any AI service.
If an LLM is used, it is always configured locally by the user (Bring Your Own Key).

---

## Installation

```bash
pip install preflights
pf start "Add authentication"
```

Or with uvx (no install needed):

```bash
uvx preflights start "Add authentication"
```

From source:

```bash
git clone https://github.com/ptngaye/preflights.git
cd preflights
pip install -e .
```

---

## Usage — the Golden Path (recommended)

By default, Preflights runs in a fully deterministic mode and does not call any external LLM.
This mode is always available and acts as a safety net.

An optional LLM-backed clarification mode can be enabled for richer question generation,
while keeping Preflights fully functional without it.

1. Run Preflights from a git repository
   ```bash
   pf start "Add OAuth authentication"
   ```

2. Answer the clarification questions
   (interactive by default, single uninterrupted flow)

3. Preflights generates documentation in `docs/`:
   - `docs/CURRENT_TASK.md` — always created
   - `docs/adr/{UID}_{slug}.md` — only if a structural decision was made
   - `docs/ARCHITECTURE_STATE.md` — regenerated when ADRs change

   Previous tasks are archived in `docs/archive/task/`.

4. Open your AI coding tool
   Tell it to implement strictly based on `CURRENT_TASK.md`.

Preflights stops here.
The AI agent implements.
No decisions happen during coding.

Session state is stored in `.preflights/` (auto-gitignored).

---

## Using Preflights with AI agents (MCP)

The CLI is the recommended entry point.

Preflights also exposes a minimal MCP server that allows AI agents to invoke it when they detect ambiguity during coding.

Typical use cases:

- An agent realizes a request implies an architectural decision
- A task is underspecified
- The agent needs explicit clarification before proceeding

In those cases, the agent can call Preflights via MCP to:

- trigger clarification
- generate ADR / TASK artifacts
- then resume implementation

**Important:**
MCP is a fallback, not a replacement for the CLI-first workflow.

---

## Claude Code

Preflights works particularly well with Claude Code:

- Run Preflights first to generate `CURRENT_TASK.md`
- Claude Code reads the task and architecture snapshot
- Claude implements without guessing or redefining scope

This keeps the agent focused on execution — not decision-making.

---

## Cursor integration

Cursor can integrate with Preflights via MCP using a dedicated adapter.

The Cursor adapter lives in a separate repository:

👉 https://github.com/ptngaye/preflights-cursor

This allows Cursor to:

- invoke Preflights when clarification is needed
- align generated code with explicit architectural decisions

Preflights does not replace Cursor Rules or `CLAUDE.md`.
It complements them by handling decisions, not coding conventions.

---

## What files are generated?

Preflights uses three explicit artifacts.

### ADR — Architecture Decision Records

Long-term, structural decisions:

- frameworks
- authentication strategy
- database choices

They are immutable, ordered, and versioned.

You don't rewrite history — you supersede it.

---

### CURRENT_TASK.md

The only thing your AI agent should implement right now.

It contains:

- goal
- context
- allowed files
- forbidden files
- acceptance criteria

If it's not in `CURRENT_TASK.md`, it shouldn't be implemented.

---

### ARCHITECTURE_STATE.md

A generated snapshot of the current architecture:

- compact
- machine-readable
- fast to scan
- never edited manually

It exists to give agents context — not to replace ADRs.

Only regenerated when an ADR is created or updated.

---

## Core concepts (human version)

- Decisions are durable → ADR
- Intentions are local → TASK
- Code is disposable → implementation

If changing something would require migration or refactoring many files:
it's probably a decision.

Otherwise:
it's just a task.

---

## Architecture (very short)

Preflights follows a strict Ports & Adapters design:

- **Core** — pure, deterministic, no I/O
- **Application** — orchestration
- **Adapters** — filesystem, LLM, clock, IDs
- **CLI** — human interface (golden path)
- **MCP** — agent fallback integration

The Core never touches the filesystem or an LLM.

---

## Design & Specifications

Preflights is driven by explicit design specifications.

This README provides a high-level overview.
Detailed behavior, contracts, and invariants live in `docs/specs/`.

These documents are the **source of truth** for:
- core behavior and invariants
- clarification flow
- LLM interaction rules
- generated artifacts (ADR, TASK, architecture state)

If you plan to contribute or extend Preflights, start with:
- `docs/specs/core-spec.md`
- `docs/specs/mock-llm-spec.md`
- `docs/specs/cli-spec.md`

---

## When not to use Preflights

You probably don't need Preflights if:

- your prompt is already a fully detailed technical spec
- the task is purely mechanical
- no architectural or structural decision is involved

Preflights is most useful when things are still fuzzy.

---

## Development & Contributing

Requirements:

- Python 3.11+
- git

Run tests:

```bash
pytest
```

Type checking:

```bash
mypy preflights/
```

Full validation:

```bash
pytest && mypy preflights/
```

Core rules:

- no I/O
- no randomness
- same input → same output
- dataclasses are frozen
- no Any types

See `CONTRIBUTING.md` and `AGENTS.md` for contributor and agent-specific instructions.

---

## License

Apache License 2.0

You can use, modify, and distribute Preflights freely —
including for commercial projects — without lock-in.

---

Preflights is not here to slow you down.
It's here to make sure speed doesn't silently destroy quality.
