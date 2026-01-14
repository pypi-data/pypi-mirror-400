# Contributing to Preflights

Thanks for your interest in contributing to Preflights.

Preflights is a design-driven project.
Code follows explicit specifications and deterministic behavior.

Please read this document before opening a PR.

---

## Source of Truth

The authoritative documentation lives in `docs/specs/`.

In particular:
- `core-spec.md` — core invariants (determinism, purity)
- `mock-llm-spec.md` — reference clarification behavior
- `cli-spec.md` — CLI behavior and golden path
- `mcp-server-spec.md` — MCP contract

If code and specs disagree, **the spec wins**.

---

## Design Principles

All contributions must respect these rules:

- No I/O in the Core
- No randomness
- Same input → same output
- Decisions are explicit and durable (ADR)
- Tasks are local and disposable
- LLMs are assistants, never authorities

---

## MockLLM & LLM Adapters

The `MockLLMAdapter` is the behavioral reference.

All LLM-backed adapters must:
- respect the same question budget (1–2 questions per turn)
- follow the same decision semantics
- never invent or guess missing values
- return “insufficient” rather than placeholders

Validation is enforced in `llm_validation.py`.

---

## Tests

New behavior must be covered by tests.

At minimum:
- no more than 2 clarification questions per turn
- `questions` and `missing_info` are always 1:1
- no placeholder values (“TBD”, “unknown”, etc.)
- deterministic outputs

---

## Submitting a PR

1. Open an issue or discussion for non-trivial changes
2. Align with existing specs (or propose a spec change first)
3. Add or update tests
4. Keep PRs focused and minimal

Preflights favors correctness and clarity over cleverness.

---

Thank you for helping keep Preflights simple, explicit, and reliable.