# PREFLIGHTS_APP_CONTRACT.md — Public API Specification

**Product:** Preflights  
**Version:** 1.0.0  
**Purpose:** Define the stable public API that all adapters (CLI, MCP Server, future UI) MUST use.  
**Stability:** This contract is FROZEN for V1. Breaking changes require major version bump.

---

## 1. Overview

**PreflightsApp** exposes exactly **2 public functions** for multi-turn clarification:

1. `start_preflight()` — Begin a new clarification session
2. `continue_preflight()` — Provide answers and progress toward completion

All adapters (CLI, MCP Server, Web UI, etc.) MUST use this contract without modification.

---

## 2. Type Definitions

### 2.1 Input Types

```python
@dataclass
class PreflightStartInput:
    """Input for starting a preflight."""
    intention: str  # User's intention text
    repo_path: str  # Absolute path to repository root
```

```python
@dataclass
class PreflightContinueInput:
    """Input for continuing a preflight."""
    session_id: str  # Session ID from start_preflight()
    answers_delta: Dict[str, Union[str, List[str]]]  # New answers (question_id -> value)
```

---

### 2.2 Output Types

```python
@dataclass
class Question:
    """A clarification question."""
    id: str  # Stable identifier (e.g., "auth_strategy")
    type: Literal["single_choice", "multi_choice", "free_text"]
    question: str  # Human-readable question text
    options: Optional[List[str]] = None  # For choice questions
    min_selections: Optional[int] = None  # For multi_choice
    max_selections: Optional[int] = None  # For multi_choice
    optional: bool = False  # If true, can be skipped
```

```python
@dataclass
class PreflightStartResult:
    """Result of start_preflight()."""
    session_id: str  # Unique session identifier
    questions: List[Question]  # Initial questions to ask
```

```python
@dataclass
class PreflightContinueResult:
    """Result of continue_preflight()."""
    status: Literal["needs_more_answers", "needs_clarification", "completed", "error"]
    
    # If status = "needs_more_answers" or "needs_clarification"
    questions: Optional[List[Question]] = None
    
    # If status = "completed"
    artifacts: Optional[PreflightArtifacts] = None
    
    # If status = "error"
    error: Optional[PreflightError] = None
```

```python
@dataclass
class PreflightArtifacts:
    """Artifacts created upon completion."""
    task_path: str  # Path to CURRENT_TASK.md (relative to repo)
    adr_path: Optional[str] = None  # Path to ADR file (if created)
    architecture_state_path: Optional[str] = None  # Path to ARCHITECTURE_STATE.md (if updated)
    agent_prompt_path: Optional[str] = None  # Path to AGENT_PROMPT.md
    agent_prompt: Optional[str] = None  # The prompt content for copy-paste
```

```python
@dataclass
class PreflightError:
    """Error details."""
    code: str  # Error code (e.g., "VALIDATION_FAILED", "SESSION_EXPIRED")
    message: str  # Human-readable error message
    details: Optional[Dict[str, Any]] = None  # Structured details
    recovery_hint: Optional[str] = None  # Suggestion for recovery
```

---

## 3. Public API

### 3.1 `start_preflight()`

**Signature:**

```python
def start_preflight(
    intention: str,
    repo_path: str
) -> PreflightStartResult:
    """
    Start a new clarification session.
    
    Args:
        intention: User's intention (e.g., "Add authentication")
        repo_path: Absolute path to repository root
    
    Returns:
        PreflightStartResult with session_id + initial questions
    
    Raises:
        PreflightError: If repo_path invalid, config malformed, etc.
    
    Side effects:
        - Creates in-memory session (30min expiry)
        - Reads repository topology (FileContext)
        - Calls LLM to generate questions
        - Does NOT modify filesystem
    
    Example:
        result = start_preflight(
            intention="Add OAuth authentication",
            repo_path="/home/user/my-project"
        )
        
        print(f"Session: {result.session_id}")
        for q in result.questions:
            print(f"  {q.question}")
    """
    ...
```

---

### 3.2 `continue_preflight()`

**Signature:**

```python
def continue_preflight(
    session_id: str,
    answers_delta: Dict[str, Union[str, List[str]]]
) -> PreflightContinueResult:
    """
    Continue clarification with new answers.
    
    Args:
        session_id: Session ID from start_preflight()
        answers_delta: New answers to provide
            Format: {
                "question_id": "single_answer",  # For single_choice / free_text
                "question_id": ["answer1", "answer2"]  # For multi_choice
            }
    
    Returns:
        PreflightContinueResult with one of:
        - status="needs_more_answers" + remaining questions
        - status="needs_clarification" + follow-up questions
        - status="completed" + artifact paths
        - status="error" + error details
    
    Raises:
        PreflightError: If session_id invalid or expired
    
    Side effects:
        - Updates in-memory session state
        - If completed:
          - Writes ADR to docs/adr/<uid>_<slug>.md (if needed)
          - Archives old CURRENT_TASK.md to docs/archive/task/
          - Writes new CURRENT_TASK.md
          - Updates ARCHITECTURE_STATE.md (if ADR created)
          - Closes session
    
    Example:
        # First call (incomplete answers)
        result = continue_preflight(
            session_id="abc-123",
            answers_delta={"auth_strategy": "OAuth"}
        )
        assert result.status == "needs_more_answers"
        
        # Second call (complete answers)
        result = continue_preflight(
            session_id="abc-123",
            answers_delta={
                "auth_library": "next-auth",
                "oauth_providers": ["Google", "GitHub"]
            }
        )
        assert result.status == "completed"
        print(f"Task: {result.artifacts.task_path}")
        print(f"ADR: {result.artifacts.adr_path}")
    """
    ...
```

---

## 4. Status Flow (State Machine)

```
┌─────────────────────┐
│  start_preflight()  │
│                     │
│  Returns:           │
│  - session_id       │
│  - questions[]      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  continue_preflight(answers_delta)  │
└──────────┬──────────────────────────┘
           │
           ▼
     ┌─────────────┐
     │   Status?   │
     └──────┬──────┘
            │
   ┌────────┼────────────┬──────────┐
   │        │            │          │
   ▼        ▼            ▼          ▼
┌──────┐ ┌─────┐ ┌──────────┐ ┌───────┐
│needs_│ │needs│ │completed │ │ error │
│more_ │ │clar-│ │          │ │       │
│answer│ │ifi- │ │ artifacts│ │ details│
│      │ │cation│ │          │ │       │
└──┬───┘ └──┬──┘ └────┬─────┘ └───────┘
   │        │         │
   │        │         │ (session closed)
   │        │         ▼
   │        │      [END]
   │        │
   └────┬───┘
        │
        ▼ (loop back)
 continue_preflight()
```

---

## 5. Status Semantics (NORMATIVE)

### 5.1 `needs_more_answers`

**Meaning:** Some required questions are still unanswered.

**Response:**
```python
{
    "status": "needs_more_answers",
    "questions": [
        # Only the UNANSWERED required questions
    ]
}
```

**Client action:** Ask user remaining questions, call `continue_preflight()` again.

---

### 5.2 `needs_clarification`

**Meaning:** All initial questions answered, but Core needs MORE information.

**Response:**
```python
{
    "status": "needs_clarification",
    "questions": [
        # NEW follow-up questions from Core
    ]
}
```

**Client action:** Ask user new questions, call `continue_preflight()` again.

**Example scenario:**
```
Initial: "Add authentication"
Q1: "OAuth or Email?" → "OAuth"
Q2: "Which library?" → "next-auth"

Core detects: "next-auth requires database session storage"
→ needs_clarification
Q3: "Database for session storage?" → "PostgreSQL"
```

---

### 5.3 `completed`

**Meaning:** Clarification complete, artifacts created and written to filesystem.

**Response:**
```python
{
    "status": "completed",
    "artifacts": {
        "task_path": "docs/CURRENT_TASK.md",
        "adr_path": "docs/adr/20250104T143512.237Z_authentication_strategy.md",
        "architecture_state_path": "docs/ARCHITECTURE_STATE.md"
    }
}
```

**Client action:** Display success, show artifact paths, end session.

**Guarantees:**
- All files exist on filesystem
- Session is closed (session_id invalid after this)
- Old CURRENT_TASK.md archived (if existed)

---

### 5.4 `error`

**Meaning:** An error occurred that prevents continuation.

**Response:**
```python
{
    "status": "error",
    "error": {
        "code": "SESSION_EXPIRED",
        "message": "Session abc-123 expired after 30 minutes",
        "recovery_hint": "Start a new session with start_preflight()"
    }
}
```

**Client action:** Display error, suggest recovery action, potentially restart.

**Common error codes:**

| Code | Meaning | Recovery |
|------|---------|----------|
| `SESSION_EXPIRED` | Session timed out (30min) | Restart with `start_preflight()` |
| `VALIDATION_FAILED` | Snapshot validation failed | Fix previous ADR manually |
| `FILESYSTEM_ERROR` | Cannot write files | Check permissions |
| `PARSE_ERROR` | Existing file malformed | Fix malformed file |
| `STATE_CORRUPTION` | Architecture state corrupted | Run repair command |
| `PATCH_EXTRACTION_FAILED` | LLM failed to extract patch | Review answers, retry |
| `INVALID_ANSWER` | Answer doesn't match question type | Provide valid answer |

---

## 6. Concurrency & Session Management

### 6.1 Session Lifecycle

**Creation:** `start_preflight()` creates a session with 30-minute expiry.

**Expiry:** Sessions expire after 30 minutes of inactivity (no `continue_preflight()` call).

**Cleanup:** Sessions are cleaned up lazily on next access or via background task.

**Concurrency:** V1 does NOT support concurrent sessions for same repo. Last write wins.

---

### 6.2 Session Isolation (NORMATIVE)

**Rule:** Each session is isolated. Multiple sessions can coexist for different repos.

```python
# Session A: /home/user/project-a
result_a = start_preflight("Add auth", "/home/user/project-a")

# Session B: /home/user/project-b
result_b = start_preflight("Add cache", "/home/user/project-b")

# Both sessions are independent
continue_preflight(result_a.session_id, {...})  # OK
continue_preflight(result_b.session_id, {...})  # OK
```

**Same repo, multiple sessions (V1 behavior):**

```python
# Session 1: start preflight
session_1 = start_preflight("Add auth", "/home/user/my-project")

# Session 2: start another preflight (SAME REPO)
session_2 = start_preflight("Add cache", "/home/user/my-project")

# Both sessions can continue independently
# But if both complete, last write wins (filesystem race)
# V1 does NOT prevent this (user responsibility)
```

**V2+ may add locking.**

---

## 7. Error Handling (Client Responsibility)

### 7.1 Retry Policy

**Transient errors (retry):**
- `FILESYSTEM_ERROR` (permissions may be fixed)
- `PATCH_EXTRACTION_FAILED` (LLM may succeed on retry)

**Permanent errors (no retry):**
- `SESSION_EXPIRED` (must restart)
- `VALIDATION_FAILED` (manual fix required)
- `STATE_CORRUPTION` (manual repair required)

**Example:**

```python
def safe_continue(session_id, answers, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = continue_preflight(session_id, answers)
            return result
        except PreflightError as e:
            if e.code in ["SESSION_EXPIRED", "VALIDATION_FAILED"]:
                raise  # Don't retry
            if attempt == max_retries - 1:
                raise  # Last attempt
            time.sleep(1)  # Backoff
```

---

### 7.2 Validation Before Calling

**Client SHOULD validate answers before calling `continue_preflight()`:**

```python
def validate_answer(question: Question, answer: Union[str, List[str]]) -> bool:
    """Validate answer matches question type and constraints."""
    
    if question.type == "single_choice":
        if not isinstance(answer, str):
            return False
        if question.options and answer not in question.options:
            return False
    
    elif question.type == "multi_choice":
        if not isinstance(answer, list):
            return False
        if question.options:
            if not all(a in question.options for a in answer):
                return False
        if question.min_selections and len(answer) < question.min_selections:
            return False
        if question.max_selections and len(answer) > question.max_selections:
            return False
    
    elif question.type == "free_text":
        if not isinstance(answer, str):
            return False
    
    return True
```

---

## 8. Adapter Implementation Checklist

Any adapter (CLI, MCP, Web UI) MUST:

- ✅ Call `start_preflight()` to begin
- ✅ Present questions to user (with type awareness: single/multi/free)
- ✅ Collect answers in correct format (str vs List[str])
- ✅ Call `continue_preflight()` with answers_delta
- ✅ Handle all 4 status values (needs_more_answers, needs_clarification, completed, error)
- ✅ Loop until status = "completed" or "error"
- ✅ Display artifact paths on completion
- ✅ Handle errors gracefully (display recovery hints)
- ✅ Respect session expiry (30 minutes)

**Must NOT:**
- ❌ Modify PreflightsApp internals
- ❌ Call Core directly (bypass PreflightsApp)
- ❌ Assume status order (e.g., always needs_more_answers before needs_clarification)
- ❌ Cache questions (always use latest from response)

---

## 9. Example Flows

### 9.1 Simple Flow (No Follow-up)

```python
# Step 1: Start
result = start_preflight("Add caching", "/home/user/project")
# result.questions = [
#   {"id": "cache_type", "type": "single_choice", "options": ["Redis", "Memcached"]},
#   {"id": "ttl", "type": "free_text", "question": "Default TTL?"}
# ]

# Step 2: Answer all
result = continue_preflight(
    result.session_id,
    {
        "cache_type": "Redis",
        "ttl": "3600"
    }
)
# result.status = "completed"
# result.artifacts.task_path = "docs/CURRENT_TASK.md"
```

---

### 9.2 Complex Flow (Follow-up Questions)

```python
# Step 1: Start
result = start_preflight("Add authentication", "/home/user/project")
# result.questions = [{"id": "auth_strategy", ...}]

# Step 2: Partial answer
result = continue_preflight(result.session_id, {"auth_strategy": "OAuth"})
# result.status = "needs_more_answers"
# result.questions = [{"id": "oauth_providers", ...}, {"id": "auth_library", ...}]

# Step 3: Complete initial questions
result = continue_preflight(
    result.session_id,
    {
        "oauth_providers": ["Google", "GitHub"],
        "auth_library": "next-auth"
    }
)
# result.status = "needs_clarification"  ← Core needs more info
# result.questions = [{"id": "session_storage", ...}]

# Step 4: Answer follow-up
result = continue_preflight(result.session_id, {"session_storage": "database"})
# result.status = "completed"
```

---

### 9.3 Error Flow

```python
# Step 1: Start
result = start_preflight("Add auth", "/home/user/project")

# Step 2: Wait 35 minutes (session expires)

# Step 3: Try to continue
result = continue_preflight(result.session_id, {"auth_strategy": "OAuth"})
# result.status = "error"
# result.error.code = "SESSION_EXPIRED"
# result.error.recovery_hint = "Start a new session..."

# Client restarts
result = start_preflight("Add auth", "/home/user/project")  # New session
```

---

## 10. Implementation Notes

### 10.1 Function Signatures (Python)

```python
from preflights.app import start_preflight, continue_preflight

# These are the ONLY public exports
__all__ = ["start_preflight", "continue_preflight"]
```

---

### 10.2 Alternative Signatures (Other Languages)

**TypeScript:**

```typescript
interface PreflightsApp {
  startPreflight(
    intention: string,
    repoPath: string
  ): Promise<PreflightStartResult>;
  
  continuePreflight(
    sessionId: string,
    answersDelta: Record<string, string | string[]>
  ): Promise<PreflightContinueResult>;
}
```

**Go:**

```go
type PreflightsApp interface {
    StartPreflight(intention string, repoPath string) (*PreflightStartResult, error)
    ContinuePreflight(sessionID string, answersDelta map[string]interface{}) (*PreflightContinueResult, error)
}
```

---

## 11. Contract Stability

**V1 Contract Guarantee:**

This API is STABLE for all V1.x releases.

**Allowed changes (backward-compatible):**
- Add optional fields to result types
- Add new error codes
- Add new question types (clients ignore unknown types)

**Breaking changes (require V2.0):**
- Change function signatures
- Remove fields from result types
- Change status enum values
- Change error code meanings

---

## 12. Summary

**Public API:**
- `start_preflight(intention, repo_path)` → session_id + questions
- `continue_preflight(session_id, answers_delta)` → status + questions/artifacts/error

**Status values:**
- `needs_more_answers` → collect remaining answers
- `needs_clarification` → ask follow-up questions
- `completed` → done, artifacts written
- `error` → something failed, check recovery_hint

**Adapters MUST:**
- Use this contract exclusively
- Handle all 4 statuses
- Loop until completed or error
- Validate answers before calling

**This contract enables:**
- CLI adapter (Golden Path)
- MCP Server adapter (Claude Code)
- Future Web UI adapter
- Future IDE plugins

**All without divergence.**

---