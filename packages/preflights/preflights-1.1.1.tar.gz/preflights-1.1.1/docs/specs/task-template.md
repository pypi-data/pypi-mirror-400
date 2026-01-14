# CURRENT_TASK.md — Task Artifact Specification V2

**Product:** Preflights
**Version:** 1.0.0  
**Artifact:** `docs/CURRENT_TASK.md`
**Purpose:** Implementation brief for coding agents

---

## 1. Overview

`CURRENT_TASK.md` is the **active implementation brief** that tells a coding agent exactly what to implement. It is:

- **Generated** by Preflights after clarification
- **Mutable** (replaced on each new preflight)
- **The single source of truth** for what the agent should implement

---

## 2. File Location

```
<repo_root>/
├── docs/
│   ├── CURRENT_TASK.md          # Active task (always here)
│   ├── AGENT_PROMPT.md          # Copy-paste prompt for agent
│   ├── ARCHITECTURE_STATE.md    # Architecture snapshot
│   ├── adr/                     # Immutable ADRs
│   └── archive/
│       └── task/                # Archived previous tasks
│           └── <UID>_<slug>.md
```

---

## 3. Task Lifecycle

```
1. User runs: pf start "Add authentication"
2. Preflight completes → CURRENT_TASK.md written
3. Previous task archived to docs/archive/task/<UID>_<slug>.md
4. Agent implements from CURRENT_TASK.md
5. Next preflight → cycle repeats
```

**There is only ONE active task at a time.**

---

## 4. Task Format

### 4.1 Header (Metadata Comments)

```markdown
<!-- UID: 20250108T120000.001Z-T001 -->
<!-- Created: 2025-01-08T12:00:00Z -->
<!-- Related ADR: 20250108T120000.000Z-A001 -->
```

| Field | Description |
|-------|-------------|
| `UID` | Unique identifier (timestamp-based) |
| `Created` | ISO 8601 UTC timestamp |
| `Related ADR` | UID of associated ADR (if any) |

### 4.2 Title

```markdown
# Add OAuth authentication
```

The title is the user's **original intention**, possibly truncated to ~80 characters.

### 4.3 Objective

```markdown
## Objective

Add OAuth authentication

Decision: Authentication - Strategy=OAuth, Library=next-auth
```

Contains:
- Original intention
- Decision patch summary (category + fields)

### 4.4 Context

```markdown
## Context

Add OAuth authentication

Related ADR: 20250108T120000.000Z-A001
```

Provides:
- Background for the implementation
- Reference to related ADR (if any)

### 4.5 Allowlist

```markdown
## Allowlist

- `src/auth/`
- `src/middleware/`
- `src/pages/api/auth/`
- `package.json`
```

**Explicitly permitted** files/directories. The agent should:
- Only modify files matching these patterns
- Ask for clarification if needing to touch other files

### 4.6 Forbidden

```markdown
## Forbidden

- `.git/`
- `node_modules/`
- `.env`
- `credentials.json`
```

**Never touch** these files. Standard forbidden patterns:
- Version control: `.git/`
- Dependencies: `node_modules/`, `vendor/`, `__pycache__/`
- Secrets: `.env*`, `credentials`, `secrets`
- Build outputs: `dist/`, `build/`, `.next/`

### 4.7 Technical Constraints

```markdown
## Technical Constraints

- Use OAuth for Strategy
- Use next-auth for Library
- CSRF protection required
- Session tokens in httpOnly cookies
```

Specific technical requirements derived from:
- Decision patch fields
- Heuristics configuration
- User answers

### 4.8 Acceptance Criteria

```markdown
## Acceptance Criteria

- [ ] OAuth flow works end-to-end
- [ ] Refresh tokens handle expiration
- [ ] Protected routes redirect to login
- [ ] Session persists across page refresh
```

Checkboxes the agent must satisfy. Implementation is complete when all are checked.

---

## 5. Complete Example

```markdown
<!-- UID: 20250108T120000.001Z-T001 -->
<!-- Created: 2025-01-08T12:00:00Z -->
<!-- Related ADR: 20250108T120000.000Z-A001 -->

# Add OAuth authentication

## Objective

Add OAuth authentication

Decision: Authentication - Strategy=OAuth, Library=next-auth

## Context

Add OAuth authentication

Related ADR: 20250108T120000.000Z-A001

## Allowlist

- `src/auth/`
- `src/middleware/`
- `src/pages/api/auth/`
- `package.json`
- `src/lib/session.ts`

## Forbidden

- `.git/`
- `node_modules/`
- `.env`
- `dist/`
- `build/`

## Technical Constraints

- Use OAuth for Strategy
- Use next-auth for Library
- CSRF protection required
- Session tokens in httpOnly cookies

## Acceptance Criteria

- [ ] OAuth flow works end-to-end with Google provider
- [ ] Refresh tokens handle expiration correctly
- [ ] Protected routes redirect unauthenticated users to login
- [ ] Session persists across page refresh
- [ ] Logout clears all session data
```

---

## 6. UID Format

```
YYYYMMDDTHHMMSS.mmmZ-XXXX
```

Example:
```
20250108T120000.001Z-T001
```

| Part | Description |
|------|-------------|
| `YYYYMMDDTHHMMSS` | UTC timestamp |
| `.mmm` | Milliseconds |
| `Z` | UTC timezone indicator |
| `-XXXX` | Suffix for uniqueness |

### 6.1 UID Rules

- Globally unique by construction
- Lexicographical ordering = chronological ordering
- No numeric sequence (no renumbering)
- Branch-safe (parallel branches won't collide)

---

## 7. Archival

When a new task is created, the previous task is archived:

```
docs/archive/task/20250107T100000.000Z-T000_previous_task.md
```

Archive filename format: `<UID>_<slug>.md`

**Archived tasks are immutable.**

---

## 8. Relationship to Other Artifacts

```
┌─────────────────────────────────────────────────────────────┐
│                     CURRENT_TASK.md                         │
│                    (Implementation Brief)                    │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │ references
                           │
┌─────────────────────────────────────────────────────────────┐
│                    ADR (if created)                         │
│                  (Architectural Decision)                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
                           │ updates
                           │
┌─────────────────────────────────────────────────────────────┐
│               ARCHITECTURE_STATE.md                         │
│                  (Generated Projection)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Agent Behavior Contract

When implementing from `CURRENT_TASK.md`, the agent **MUST**:

1. Read `docs/ARCHITECTURE_STATE.md` first (understand current decisions)
2. Read `docs/CURRENT_TASK.md` (understand scope)
3. Only modify files in **Allowlist**
4. Never touch files in **Forbidden**
5. Follow **Technical Constraints**
6. Complete all **Acceptance Criteria**
7. If hitting ambiguity → request new preflight (not invent decisions)

---

## 10. Validation Rules

| Rule | Description |
|------|-------------|
| UID format | Must match `YYYYMMDDTHHMMSS.mmmZ-XXXX` |
| Title present | Must have H1 title |
| Objective present | Must have objective section |
| Allowlist non-empty | At least one allowed path |
| Forbidden non-overlapping | No path in both Allowlist and Forbidden |
| Acceptance criteria present | At least one criterion |
