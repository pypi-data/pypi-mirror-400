# ARCHITECTURE_STATE.md — Architecture Snapshot Specification V2

**Product:** Preflights
**Version:** 1.0.0  
**Artifact:** `docs/ARCHITECTURE_STATE.md`
**Purpose:** Current architecture decisions snapshot (read-only projection)

---

## 1. Overview

`ARCHITECTURE_STATE.md` is a **generated projection** of the current architecture based on all ADRs. It provides:

- Quick reference for humans
- Machine-readable context for coding agents
- Current state without reading all ADRs

**Critical:** This file is **never** a source of truth. It can be deleted and regenerated at any time from ADRs.

---

## 2. File Location

```
<repo_root>/
├── docs/
│   ├── ARCHITECTURE_STATE.md    # Generated projection
│   ├── CURRENT_TASK.md
│   ├── AGENT_PROMPT.md
│   └── adr/
│       ├── 20250101T..._initial.md
│       ├── 20250105T..._database.md
│       └── 20250108T..._auth.md    # ← Source of truth
```

---

## 3. Generation Rules

### 3.1 When Generated

- **Created** when first ADR is written
- **Updated** when new ADR is written
- **Regenerated** from latest ADR's snapshot section

### 3.2 Source of Truth

The snapshot comes from **PART 1** of the most recent ADR:

```markdown
# ADR-XXX: Authentication Strategy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 1: ARCHITECTURE SNAPSHOT         ← This is extracted
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## CURRENT ARCHITECTURE STATE
...
```

---

## 4. Format

### 4.1 Header (Metadata Comments)

```markdown
<!-- UID: 20250108T120000.000Z-A001 -->
<!-- Schema: v1 -->
```

| Field | Description |
|-------|-------------|
| `UID` | UID of the ADR this was generated from |
| `Schema` | Schema version |

### 4.2 Title and Description

```markdown
# Architecture State

Current architecture decisions snapshot.
```

### 4.3 Categories

Each category represents a domain of decisions:

```markdown
## Categories

### Authentication
- **Strategy**: OAuth (ADR 20250108T120000.000Z-A001)
- **Library**: next-auth (ADR 20250108T120000.000Z-A001)

### Database
- **Type**: PostgreSQL (ADR 20250105T090000.000Z-A000)
- **ORM**: Prisma (ADR 20250105T090000.000Z-A000)

### Frontend
- **Framework**: Next.js (ADR 20250101T120000.000Z-A000)
- **Styling**: Tailwind CSS (ADR 20250101T120000.000Z-A000)
```

---

## 5. Complete Example

```markdown
<!-- UID: 20250108T120000.000Z-A001 -->
<!-- Schema: v1 -->

# Architecture State

Current architecture decisions snapshot.

## Categories

### Frontend
- **Framework**: Next.js 14 (ADR 20250101T120000.000Z-A000)
- **Styling**: Tailwind CSS (ADR 20250101T120000.000Z-A000)
- **State Management**: Zustand (ADR 20250103T140000.000Z-A000)

### Backend
- **Runtime**: Node.js 20 (ADR 20250101T120000.000Z-A000)
- **Framework**: Next.js API Routes (ADR 20250101T120000.000Z-A000)

### Database
- **Type**: PostgreSQL 15 (ADR 20250105T090000.000Z-A000)
- **ORM**: Prisma (ADR 20250105T090000.000Z-A000)
- **Hosting**: Supabase (ADR 20250105T090000.000Z-A000)

### Authentication
- **Strategy**: OAuth (ADR 20250108T120000.000Z-A001)
- **Library**: next-auth (ADR 20250108T120000.000Z-A001)
- **Providers**: Google, GitHub (ADR 20250108T120000.000Z-A001)

### Infra
- **Hosting**: Vercel (ADR 20250101T120000.000Z-A000)
- **CI/CD**: GitHub Actions (ADR 20250101T120000.000Z-A000)
```

---

## 6. Default Schema (V1)

### 6.1 Categories

| Category | Description | Common Fields |
|----------|-------------|---------------|
| Frontend | UI layer decisions | Framework, Styling, State Management |
| Backend | Server-side decisions | Runtime, Framework, API Style |
| Database | Data storage decisions | Type, ORM, Hosting |
| Authentication | Auth decisions | Strategy, Library, Providers |
| Infra | Infrastructure decisions | Hosting, CI/CD, Monitoring |
| Other | Catch-all for edge cases | (any field) |

### 6.2 Field Naming

- PascalCase: `Strategy`, `Framework`, `Library`
- Descriptive: Name should be self-explanatory
- Stable: Don't rename fields between ADRs

---

## 7. Category Evolution

### 7.1 Adding New Categories

When a new domain of decisions is introduced:

1. New ADR creates category with initial fields
2. ARCHITECTURE_STATE is regenerated
3. Category appears in snapshot

### 7.2 Modifying Categories

When an existing category is updated:

1. New ADR modifies specific fields
2. Previous values are recorded as "was: X"
3. ARCHITECTURE_STATE shows new values only

### 7.3 History

ARCHITECTURE_STATE does **not** show history. For history:
- Read individual ADRs
- Check "Changes in this version" section of ADRs

---

## 8. ADR Reference Format

Each field includes an ADR reference:

```markdown
- **Strategy**: OAuth (ADR 20250108T120000.000Z-A001)
```

Format: `(ADR <UID>)`

This allows:
- Traceability to original decision
- Quick navigation to rationale
- Audit trail

---

## 9. Reading from Code

The architecture state can be read programmatically:

```python
# Via MCP tool
result = await mcp.call_tool("read_architecture", {})

# Returns:
{
    "status": "success",
    "architecture": {
        "uid": "20250108T120000.000Z-A001",
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

---

## 10. Relationship to ADRs

```
┌─────────────────────────────────────────────────────────────┐
│                        ADR Chain                            │
│                                                             │
│  ADR-001 → ADR-002 → ADR-003 → ADR-004 (latest)            │
│                                    │                        │
│                                    │ PART 1 extracted       │
│                                    ▼                        │
│                        ARCHITECTURE_STATE.md                │
│                         (generated projection)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Validation Rules

| Rule | Description |
|------|-------------|
| UID present | Must reference source ADR |
| Schema version | Must specify schema version |
| Categories valid | All categories in V1 schema |
| Fields valid | All fields valid for category |
| ADR references valid | All ADR UIDs exist |

---

## 12. Agent Behavior

When reading ARCHITECTURE_STATE.md, agents should:

1. **Trust** the snapshot as current state
2. **Follow** documented decisions
3. **Not contradict** existing architecture
4. **Reference** when making related changes
5. **Request clarification** if needing to change architecture

If a change requires modifying existing architecture:
- Run new preflight
- Document decision in new ADR
- Let Preflights regenerate the snapshot
