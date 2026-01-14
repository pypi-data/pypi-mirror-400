# CURSOR_ADAPTER_V2.md — Cursor Integration Specification

**Product:** Preflights
**Version:** 1.0.0  
**Purpose:** Cursor IDE integration via MCP + repository-level configuration
**Philosophy:** Repo-native integration, no IDE extension required

---

## 1. Definition: What "Cursor Adapter" Means

Cursor Adapter V2 = **documentation + configuration + rules** so Cursor can:

- Start Preflights clarification via MCP tool `require_clarification`
- Read current architecture via MCP tool `read_architecture`
- Enforce the workflow: "no code changes unless CURRENT_TASK.md exists"
- Keep Core isolated (Ports & Adapters spec unchanged)

**No IDE plugin, no UI extension, no Cursor-specific codegen.**
The integration is repo-native + MCP-standard.

---

## 2. Deliverables

### 2.1 File Structure

```
integrations/
└── cursor/
    ├── README.md                           # Setup instructions
    ├── cursor-mcp.json                     # MCP server configuration
    ├── cursorrules.template                # .cursorrules template
    └── prompts/
        ├── cursor_system_instructions.md   # System prompt for Cursor
        └── cursor_user_prompt_template.md  # User prompt template
```

### 2.2 Repository Root

```
README.md                                   # Add "Using with Cursor" section
```

---

## 3. User Workflow

### 3.1 Setup (One-Time)

1. Install Preflights CLI: `uvx preflights` or `pip install preflights`
2. Copy `cursor-mcp.json` to Cursor's MCP configuration
3. Copy `cursorrules.template` to `.cursorrules` in repository
4. Ensure `preflights-mcp` is available on PATH

### 3.2 Daily Usage

```
1. User opens repository in Cursor
2. User asks: "Add authentication to the app"
3. Cursor checks: docs/CURRENT_TASK.md exists?
   ├── No → Call require_clarification via MCP
   │        → Display questions to user
   │        → User answers
   │        → Artifacts generated
   └── Yes → Read CURRENT_TASK.md + ARCHITECTURE_STATE.md
             → Implement strictly from brief
4. If ambiguity during implementation → trigger new clarification
```

### 3.3 Key Invariant

Cursor must **not "invent" decisions**. It must either:
- Implement strictly from `CURRENT_TASK.md` (+ `ARCHITECTURE_STATE.md`)
- Trigger clarification via MCP

---

## 4. MCP Configuration

### 4.1 cursor-mcp.json

```json
{
  "mcpServers": {
    "preflights": {
      "command": "preflights-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

### 4.2 Configuration Notes

| Setting | Description |
|---------|-------------|
| `command` | MCP server executable |
| `args` | Command-line arguments (none needed) |
| `env` | Environment variables (LLM keys if needed) |

The MCP server uses `os.getcwd()` as default repository path.
If Cursor runs from a different directory, use `repo_path` in tool calls.

---

## 5. Cursor Rules (Guardrails)

### 5.1 cursorrules.template

```markdown
# Preflights Integration Rules

## Core Principles

1. **Never invent architecture decisions**
   - All architectural choices must be documented in ADRs
   - If unclear about approach, trigger Preflights clarification

2. **Task-driven implementation**
   - Only implement what's in docs/CURRENT_TASK.md
   - Respect Allowlist and Forbidden sections
   - Complete all Acceptance Criteria

3. **Read before writing**
   - Always read docs/ARCHITECTURE_STATE.md first
   - Understand existing decisions before making changes

## When to Call Preflights

Call `require_clarification` when:
- docs/CURRENT_TASK.md does not exist
- docs/CURRENT_TASK.md is empty
- User asks for architectural decision
- Scope is unclear or missing acceptance criteria
- Implementation requires touching forbidden files

## Artifacts Reference

- `docs/CURRENT_TASK.md` — Current implementation brief
- `docs/ARCHITECTURE_STATE.md` — Architecture decisions snapshot
- `docs/adr/` — Immutable decision records
- `docs/AGENT_PROMPT.md` — Copy-paste prompt (CLI output)

## MCP Tools Available

1. `require_clarification`
   - Start or continue clarification session
   - Generates TASK + ADR artifacts

2. `read_architecture`
   - Read current architecture snapshot
   - Returns categories and decisions

## Example Workflow

User: "Add OAuth authentication"

1. Check: Does docs/CURRENT_TASK.md exist?
2. If no: Call require_clarification(user_intention="Add OAuth authentication")
3. Display questions, collect answers
4. Once completed: Read docs/CURRENT_TASK.md
5. Implement strictly within scope
```

---

## 6. Prompt Templates

### 6.1 System Instructions

**File:** `prompts/cursor_system_instructions.md`

```markdown
You are a coding assistant integrated with Preflights.

## Rules

1. Before making any code changes, verify docs/CURRENT_TASK.md exists
2. If no task exists, use the `require_clarification` MCP tool
3. Always respect the Allowlist and Forbidden sections
4. Never introduce architectural decisions not documented in ADRs
5. If hitting ambiguity, request new clarification rather than guessing

## Reading Order

1. docs/ARCHITECTURE_STATE.md (understand current state)
2. docs/CURRENT_TASK.md (understand scope)
3. Relevant ADRs if referenced

## MCP Tools

- require_clarification: Start/continue clarification
- read_architecture: Get current architecture state
```

### 6.2 User Prompt Template

**File:** `prompts/cursor_user_prompt_template.md`

```markdown
## Quick Start

After Preflights completes, paste the content of `docs/AGENT_PROMPT.md` here.

## Minimal Prompt (Alternative)

If you don't want to open files:

```
Read docs/CURRENT_TASK.md and docs/ARCHITECTURE_STATE.md, then implement the task following the constraints and acceptance criteria.
```

## Full Prompt (Copy from AGENT_PROMPT.md)

The AGENT_PROMPT.md file contains:
- Task file path
- Architecture state path
- ADR path (if applicable)
- Instructions for implementation
```

---

## 7. Setup Instructions (README.md)

### 7.1 integrations/cursor/README.md

```markdown
# Cursor Integration for Preflights

## What This Integration Does

- MCP server for Preflights tools
- Guardrails to prevent architecture drift
- Seamless clarification workflow

## Requirements

- Preflights CLI installed: `pip install preflights`
- `preflights-mcp` available on PATH

## Setup Steps

### 1. Configure MCP Server

Copy `cursor-mcp.json` content to your Cursor MCP configuration.

Location varies by OS:
- macOS: `~/Library/Application Support/Cursor/mcp.json`
- Windows: `%APPDATA%\Cursor\mcp.json`
- Linux: `~/.config/cursor/mcp.json`

### 2. Add Repository Rules

Copy `cursorrules.template` to `.cursorrules` in your repository root.

### 3. Verify Setup

In Cursor, try asking: "What MCP tools are available?"
You should see `require_clarification` and `read_architecture`.

## Usage

### Starting Implementation

1. Ask Cursor: "Add [feature description]"
2. If no CURRENT_TASK.md exists, Cursor will call `require_clarification`
3. Answer the questions
4. Once completed, Cursor implements from the task brief

### Reading Architecture

Ask Cursor: "What's the current architecture?"
Cursor will call `read_architecture` and display the snapshot.

## Troubleshooting

### "repo targeting" Issues

If Cursor can't find the repository:
1. Ensure Cursor launches MCP server from workspace root
2. Or pass `repo_path` explicitly in tool calls

### MCP Server Not Found

Ensure `preflights-mcp` is on PATH:
```bash
which preflights-mcp  # Should return a path
```

If not installed:
```bash
pip install preflights
```
```

---

## 8. Non-Goals (Explicit)

| Non-Goal | Reason |
|----------|--------|
| Cursor extension/plugin | Keep it simple, repo-native |
| Code generation | Preflights clarifies, doesn't generate code |
| Duplicate Core rules | Guardrails only, Core stays isolated |
| Third tool `validate_task` | Keep MCP to 2 tools |

---

## 9. Acceptance Criteria

| Criterion | Verification |
|-----------|--------------|
| `integrations/cursor/` exists | Directory present |
| README references Cursor integration | Link in root README |
| Integration doc is actionable | Developer can configure in < 5 min |
| No Core changes | Tests still pass |
| MCP tools work from Cursor | Manual verification |

---

## 10. Future Considerations

### 10.1 LLM Configuration in Cursor

Users can add LLM API keys to MCP server environment:

```json
{
  "mcpServers": {
    "preflights": {
      "command": "preflights-mcp",
      "env": {
        "PREFLIGHTS_LLM_PROVIDER": "anthropic",
        "PREFLIGHTS_ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### 10.2 Workspace-Specific Configuration

For monorepos with multiple projects, use `repo_path` in tool calls:

```json
{
  "user_intention": "Add authentication",
  "repo_path": "/workspace/packages/my-app"
}
```
