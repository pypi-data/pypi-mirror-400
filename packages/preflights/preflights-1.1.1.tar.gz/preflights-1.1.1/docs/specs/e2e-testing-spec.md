# TEST_E2E_GOLDEN_PATH_V2.md — End-to-End Test Specification

**Product:** Preflights
**Version:** 1.0.0  
**Purpose:** E2E test specification for Golden Path validation
**Location:** `tests/cli/test_golden_path_e2e.py`

---

## 1. Overview

The Golden Path E2E tests validate the complete user journey:
1. User runs `pf start "<intention>"`
2. Answers questions interactively
3. Artifacts are generated correctly
4. Session is cleaned up

---

## 2. Test Environment

### 2.1 Setup

```python
@pytest.fixture
def repo_root(tmp_path):
    """Create temporary git repository."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo)
    return repo
```

### 2.2 CLI Invocation

```python
from click.testing import CliRunner
from preflights.cli.main import cli

runner = CliRunner()
result = runner.invoke(cli, ["start", "Add authentication"], input=user_input)
```

---

## 3. Test Cases

### 3.1 Happy Path: Interactive Session Creates Artifacts

**Test ID:** `test_pf_interactive_golden_path_creates_artifacts`

**Scenario:**
```
Given: Empty git repository
When: User runs `pf start "Add user authentication"`
And: Answers all questions with valid responses
Then: Exit code is 0
And: docs/CURRENT_TASK.md is created
And: docs/adr/*.md is created (if ADR needed)
And: docs/ARCHITECTURE_STATE.md is created (if ADR needed)
And: docs/AGENT_PROMPT.md is created
And: .preflights/ directory exists
And: .preflights/ is in .gitignore
```

**Input Simulation:**
```python
user_input = "\n".join([
    "1",          # auth_strategy: OAuth
    "1",          # auth_library: next-auth
]) + "\n"
```

**Assertions:**
```python
assert result.exit_code == 0
assert (repo_root / "docs" / "CURRENT_TASK.md").exists()
assert (repo_root / "docs" / "AGENT_PROMPT.md").exists()
assert (repo_root / ".preflights").exists()
assert ".preflights/" in (repo_root / ".gitignore").read_text()
```

---

### 3.2 Repo Auto-Discovery from Subdirectory

**Test ID:** `test_pf_discovers_repo_from_subdirectory`

**Scenario:**
```
Given: Git repository at /tmp/repo
And: Current directory is /tmp/repo/src/components
When: User runs `pf start "Add feature"`
Then: Artifacts are written to /tmp/repo/docs/
```

**Setup:**
```python
workdir = repo_root / "src" / "components"
workdir.mkdir(parents=True)
monkeypatch.chdir(workdir)
```

---

### 3.3 Session Expiration

**Test ID:** `test_pf_session_expires_after_30_minutes`

**Scenario:**
```
Given: Active session started
When: 30 minutes pass without activity
Then: Session is expired
And: User receives SESSION_EXPIRED error
And: Recovery hint suggests `pf resume`
```

---

### 3.4 "Other (specify)" Flow

**Test ID:** `test_pf_other_specify_collects_custom_value`

**Scenario:**
```
Given: Question with options including "Other (specify)"
When: User selects "Other (specify)"
And: User enters custom value "Custom SAML"
Then: Answer is recorded as custom value
And: Decision patch contains custom value
```

**Input Simulation:**
```python
user_input = "\n".join([
    "4",           # Select "Other (specify)"
    "Custom SAML", # Custom value
    "1",           # auth_library: next-auth
]) + "\n"
```

---

### 3.5 Non-Interactive Mode

**Test ID:** `test_pf_non_interactive_shows_questions_and_exits`

**Scenario:**
```
Given: Empty git repository
When: User runs `pf start "Add auth" --non-interactive`
Then: Questions are displayed
And: Exit code is 0 (not error)
And: No artifacts created yet
And: Session is stored for later continuation
```

---

### 3.6 JSON Output Mode

**Test ID:** `test_pf_json_output_is_machine_readable`

**Scenario:**
```
Given: Empty git repository
When: User runs `pf start "Add auth" --json`
Then: Output is valid JSON
And: Contains "status", "session_id", "questions" fields
```

**Assertion:**
```python
import json
output = json.loads(result.output)
assert output["status"] == "started"
assert "session_id" in output
assert "questions" in output
```

---

### 3.7 LLM Fallback Warning

**Test ID:** `test_pf_llm_fallback_shows_warning`

**Scenario:**
```
Given: --llm flag specified
And: No valid API key in environment
When: User runs `pf start "Add auth" --llm`
Then: Warning is displayed about fallback
And: Session continues with mock LLM
```

**Assertion:**
```python
assert "Warning" in result.output or "warning" in result.output.lower()
assert result.exit_code == 0  # Still succeeds
```

---

### 3.8 LLM Strict Mode Failure

**Test ID:** `test_pf_llm_strict_fails_without_credentials`

**Scenario:**
```
Given: --llm-strict flag specified
And: No valid API key in environment
When: User runs `pf start "Add auth" --llm --llm-strict`
Then: Error is returned
And: Exit code is non-zero
```

---

### 3.9 Answer Command

**Test ID:** `test_pf_answer_continues_session`

**Scenario:**
```
Given: Active session with pending questions
When: User runs `pf answer auth_strategy=OAuth auth_library=next-auth`
Then: Answers are recorded
And: If all questions answered, artifacts are created
```

---

### 3.10 Resume After Interruption

**Test ID:** `test_pf_resume_restarts_with_last_intention`

**Scenario:**
```
Given: Previous session that was interrupted
And: last_intention.txt contains "Add authentication"
When: User runs `pf resume`
Then: New session starts with same intention
And: Questions are displayed again
```

---

### 3.11 Reset Clears Session

**Test ID:** `test_pf_reset_clears_session`

**Scenario:**
```
Given: Active session
When: User runs `pf reset --force`
Then: session.json is deleted
And: Subsequent `pf status` shows no active session
```

---

## 4. Artifact Validation

### 4.1 CURRENT_TASK.md Structure

```python
def validate_task(path: Path):
    content = path.read_text()
    assert "<!-- UID:" in content
    assert "## Objective" in content
    assert "## Allowlist" in content
    assert "## Forbidden" in content
    assert "## Acceptance Criteria" in content
```

### 4.2 ADR Structure

```python
def validate_adr(path: Path):
    content = path.read_text()
    assert "<!-- UID:" in content
    assert "PART 1: ARCHITECTURE SNAPSHOT" in content
    assert "PART 2: DECISION DETAILS" in content
    assert "## Context" in content
    assert "## Decision" in content
```

### 4.3 ARCHITECTURE_STATE.md Structure

```python
def validate_architecture_state(path: Path):
    content = path.read_text()
    assert "<!-- UID:" in content
    assert "## Categories" in content
```

---

## 5. Edge Cases

### 5.1 Empty Intention

```python
def test_empty_intention_fails():
    result = runner.invoke(cli, ["start", ""])
    assert result.exit_code != 0
```

### 5.2 No Git Repository

```python
def test_no_git_repo_fails(tmp_path):
    # tmp_path without git init
    result = runner.invoke(cli, ["start", "Add auth"], obj={"cwd": tmp_path})
    assert "NOT_A_REPOSITORY" in result.output or result.exit_code != 0
```

### 5.3 Concurrent Sessions

```python
def test_cannot_start_second_session():
    # Start first session
    runner.invoke(cli, ["start", "First task"], input="1\n1\n")
    # Don't complete it, try to start second
    result = runner.invoke(cli, ["start", "Second task"])
    assert "active session" in result.output.lower() or result.exit_code != 0
```

---

## 6. Test Markers

```python
@pytest.mark.e2e           # End-to-end test
@pytest.mark.slow          # Takes > 1 second
@pytest.mark.integration   # Requires file system
```

---

## 7. Running Tests

```bash
# All E2E tests
pytest tests/cli/test_golden_path_e2e.py -v

# With markers
pytest -m e2e -v

# Specific test
pytest tests/cli/test_golden_path_e2e.py::test_pf_interactive_golden_path_creates_artifacts -v
```

---

## 8. Mock LLM Behavior

E2E tests use `MockLLMAdapter` by default:

| Intention Keywords | Questions Generated | Decision Hint |
|-------------------|---------------------|---------------|
| `auth`, `login`, `oauth` | auth_strategy, auth_library | `adr` |
| `database`, `db`, `sql` | db_type, db_orm | `adr` |
| `frontend`, `ui`, `react` | frontend_framework, styling | `task` |
| (other) | category, description | `unsure` |

This ensures deterministic, reproducible tests.
