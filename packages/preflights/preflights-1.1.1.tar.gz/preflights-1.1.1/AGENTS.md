# AGENTS.md — Preflights (Core + App + CLI)

> **Extends:** `../../AGENTS.md` (global rules apply)

---

## Project

**Preflights** — Clarity engine for AI-assisted development (decide → specify → implement)

**Stack:** Python 3.11+, Ports & Adapters, CLI-first, MCP adapter

**Primary goal (V1):** Golden Path interactive CLI must work end-to-end and write artifacts under `docs/`

---

## Commands

**Preferred (recommended):**
```bash
# Run CLI (installed)
uvx preflights start "Add user authentication"
pf start "Add user authentication"

# Tests
pytest

# Type-check
mypy preflights/

# Full validation
pytest && mypy preflights/
```

**From source (dev):**
```bash
# Activate venv
source .venv/bin/activate

# Run CLI
python -m preflights.cli.main start "Add user authentication"

# Tests (all)
pytest

# Tests (E2E only)
pytest tests/cli/test_golden_path_e2e.py
```

---

## Golden Path (must stay working)

```bash
pf start "<intention>"
# Answer interactively until status = completed
```

**Expected artifacts:**
- `docs/CURRENT_TASK.md` (always)
- `docs/adr/*.md` (if ADR needed)
- `docs/ARCHITECTURE_STATE.md` (if ADR created/updated)

**State:**
- `.preflights/` — ephemeral session state (auto-gitignored)

---

## Structure

```
preflights/
├── core/           # Pure logic (stateless, deterministic, NO I/O)
├── application/    # Orchestration (PreflightsApp)
├── adapters/       # I/O (filesystem, UID, clock, LLM, sessions)
├── cli/            # CLI interface (Click)
└── mcp/            # MCP Server adapter
tests/              # Test suite
docs/               # Specs (repo) + generated artifacts (user repos)
```

---

## Architecture (Ports & Adapters)

| Layer | Responsibility | I/O Allowed |
|-------|----------------|-------------|
| `core/` | Pure business logic | **NO** |
| `application/` | Orchestration | Via adapters |
| `adapters/` | I/O (FS, LLM, UID, Clock) | **YES** |
| `cli/` | User interface | Via adapters |
| `mcp/` | MCP JSON-RPC | Via adapters |

---

## Critical Rules

### Core MUST be Pure
```python
# FORBIDDEN in core/
datetime.now()          # Non-deterministic
open("file.txt")        # I/O
os.listdir(".")         # Filesystem
uuid.uuid4()            # Random
import anthropic        # External services
```

### Determinism
Same inputs → Same outputs (always)

### UX Isolation
CLI UX features (e.g., "Other (specify)" option) must NOT leak into Core.
Core receives normalized answers only.

---

## Conventions

- Frozen dataclasses for core domain types
- Typed errors (no generic exceptions)
- No mocks in core tests (pure logic)
- UIDs and timestamps always injected

---

## Prohibitions

- No I/O in `core/`
- No LLM calls in `core/`
- No mocks in core tests
- No `Any` types
- No framework coupling in core
