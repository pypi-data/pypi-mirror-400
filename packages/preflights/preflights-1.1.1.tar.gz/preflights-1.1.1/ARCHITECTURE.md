# Architecture Overview

Preflights follows a strict Ports & Adapters architecture.

This document is a high-level orientation.
Detailed behavior and contracts live in `docs/specs/`.

---

## Layers

- **Core**
    - Pure, deterministic logic
    - No I/O, no time, no randomness
    - Defines invariants and decision rules

- **Application**
    - Orchestrates workflows
    - Manages sessions and state transitions

- **Adapters**
    - Filesystem
    - LLM providers
    - Clock, IDs
    - Validation and normalization

- **Interfaces**
    - CLI (golden path)
    - MCP server (agent fallback)

---

## Key Principles

- The Core never depends on adapters
- The MockLLMAdapter defines reference behavior
- LLMs assist clarification, never make decisions
- Generated artifacts (ADR, TASK) are the contract with AI agents

---

## Where to go next

For authoritative details, see:
- `docs/specs/core-spec.md`
- `docs/specs/mock-llm-spec.md`
- `docs/specs/cli-spec.md`