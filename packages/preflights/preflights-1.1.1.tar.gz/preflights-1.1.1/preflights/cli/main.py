"""Preflights CLI entry point.

Implements CLI SPECS.md and INTERACTIVE_MODE_CLI.md:
- Interactive by default (pf start "<intention>" runs full flow)
- Non-interactive with --non-interactive or --json
- Implicit session management, human-friendly output
- 1:1 mapping to PREFLIGHTS_APP_CONTRACT
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import click

from preflights.cli.errors import (
    CLIError,
    ExitCode,
    InvalidAnswerError,
    NoActiveSessionError,
    NoPreviousSessionError,
    NotARepositoryError,
    SessionAlreadyActiveError,
    SessionExpiredError,
)
from preflights.cli.output import (
    OTHER_SPECIFY,
    print_app_error,
    print_completed,
    print_error,
    print_llm_fallback_warning,
    print_needs_clarification,
    print_needs_more_answers,
    print_start_success,
    print_status,
)
from preflights.cli.prompts import prompt_all_questions
from preflights.cli.repo import get_repo_root
from preflights.cli.state import (
    SessionState,
    StoredQuestion,
    delete_session,
    load_last_intention,
    load_session,
    save_last_intention,
    save_session,
    session_exists,
    update_session_answers,
    update_session_questions,
)
from preflights.cli.validation import parse_key_value_answers, validate_answer

if TYPE_CHECKING:
    from preflights.application.types import Question

# Session duration in minutes
SESSION_DURATION_MINUTES = 30


def _lazy_cleanup_sessions() -> None:
    """
    Best-effort cleanup of expired sessions.

    Called at the start of each CLI command to prevent accumulation.
    Failures are silently ignored (non-blocking).
    """
    import time

    try:
        from preflights.adapters.file_session import FileSessionAdapter

        adapter = FileSessionAdapter()
        adapter.cleanup_expired(time.time())
    except Exception:
        # Best effort - don't block user if cleanup fails
        pass


def _questions_to_stored(questions: tuple[Any, ...]) -> list[StoredQuestion]:
    """Convert Application questions to stored questions."""
    result = []
    for q in questions:
        stored = StoredQuestion(
            id=q.id,
            type=q.type,
            question=q.question,
            options=q.options,
            min_selections=q.min_selections,
            max_selections=q.max_selections,
            optional=q.optional,
            depends_on_question_id=getattr(q, "depends_on_question_id", None),
            depends_on_value=getattr(q, "depends_on_value", None),
        )
        result.append(stored)
    return result


def _create_session_state(
    session_id: str,
    intention: str,
    questions: tuple[Any, ...],
) -> SessionState:
    """Create new session state."""
    now = datetime.now(timezone.utc)
    expires = now.timestamp() + (SESSION_DURATION_MINUTES * 60)
    expires_dt = datetime.fromtimestamp(expires, timezone.utc)

    return SessionState(
        session_id=session_id,
        intention=intention,
        started_at=now.isoformat().replace("+00:00", "Z"),
        expires_at=expires_dt.isoformat().replace("+00:00", "Z"),
        expires_at_unix=expires,
        questions=_questions_to_stored(questions),
        answers={},
    )


def _run_interactive_loop(repo_root: str, state: SessionState) -> None:
    """
    Run the interactive question-answer loop until completed or error.

    This is the core of interactive mode:
    1. Display questions
    2. Collect answers via prompts
    3. Call continue_preflight
    4. Repeat until completed or error
    """
    from preflights.application import continue_preflight

    while True:
        # Get unanswered questions (excluding __other conditional questions)
        unanswered = [
            q for q in state.questions
            if q.id not in state.answers and q.depends_on_question_id is None
        ]

        if not unanswered:
            # All questions answered, but we still need to call continue_preflight
            # This handles the case where all initial questions are answered
            # but we might get follow-up questions
            pass

        # Prompt for answers if there are unanswered questions
        if unanswered:
            click.echo("")
            click.echo(click.style("Please answer the following questions:", bold=True))
            answers_delta = prompt_all_questions(unanswered)

            if not answers_delta:
                click.echo(click.style("No answers provided. Please try again.", fg="yellow"))
                continue

            # Update session with new answers
            state.answers.update(answers_delta)
            save_session(repo_root, state)
        else:
            # No unanswered questions, use empty delta to trigger completion check
            answers_delta = {}

        # Call Application API
        result = continue_preflight(state.session_id, answers_delta)

        # Handle result
        if result.status == "needs_more_answers":
            # Update questions in session
            if result.questions:
                new_questions = _questions_to_stored(result.questions)
                update_session_questions(repo_root, new_questions)
            state = load_session(repo_root)
            # Continue loop to ask remaining questions
            continue

        elif result.status == "needs_clarification":
            # Add new questions to session
            if result.questions:
                new_questions = _questions_to_stored(result.questions)
                update_session_questions(repo_root, new_questions)
                click.echo("")
                click.echo(click.style("Follow-up questions needed:", fg="yellow"))
            state = load_session(repo_root)
            # Continue loop to ask new questions
            continue

        elif result.status == "completed":
            # Session complete, cleanup
            delete_session(repo_root)
            click.echo("")
            if result.artifacts:
                print_completed(
                    result.artifacts.task_path,
                    result.artifacts.adr_path,
                    result.artifacts.architecture_state_path,
                    result.artifacts.agent_prompt_path,
                    result.artifacts.agent_prompt,
                    json_output=False,
                )
            else:
                print_completed("docs/CURRENT_TASK.md", None, None, None, None, json_output=False)
            return

        elif result.status == "error":
            if result.error:
                click.echo("")
                print_app_error(
                    result.error.code,
                    result.error.message,
                    result.error.recovery_hint,
                    json_output=False,
                )
            sys.exit(ExitCode.SYSTEM_ERROR)


# Click CLI application
@click.group()
@click.version_option(version="1.0.0", prog_name="preflights")
def app() -> None:
    """Preflights - Architecture Decision Automation."""
    pass


# =============================================================================
# preflights start
# =============================================================================
@app.command()
@click.argument("intention")
@click.option(
    "--repo-path",
    default=None,
    help="Repository path (default: auto-discovery via .git)",
)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Show questions and exit (for scripts/CI)",
)
@click.option("--json", "json_output", is_flag=True, help="Output machine-readable JSON (implies --non-interactive)")
@click.option(
    "--llm",
    is_flag=True,
    help="Enable real LLM provider (requires API key in environment)",
)
@click.option(
    "--llm-strict",
    is_flag=True,
    help="Fail on LLM errors instead of falling back to mock",
)
@click.option(
    "--llm-provider",
    type=click.Choice(["anthropic", "openai", "openrouter"]),
    default=None,
    help="Override LLM provider (implies --llm)",
)
def start(
    intention: str,
    repo_path: str | None,
    non_interactive: bool,
    json_output: bool,
    llm: bool,
    llm_strict: bool,
    llm_provider: str | None,
) -> None:
    """Start a new preflight session.

    INTENTION is the user's goal (e.g., "Add OAuth authentication").

    By default, runs in interactive mode: asks questions and collects answers
    until the preflight is complete.

    Use --non-interactive or --json for scripts and CI.

    Use --llm to enable real LLM providers (requires API key).
    Use --llm-strict to fail on LLM errors instead of falling back to mock.
    """
    # --json implies non-interactive
    if json_output:
        non_interactive = True

    # --llm-provider implies --llm
    if llm_provider:
        llm = True

    try:
        # 0. Lazy cleanup of expired sessions (best effort)
        _lazy_cleanup_sessions()

        # 1. Discover repository root
        repo_root = get_repo_root(repo_path)

        # 2. Check for existing session
        if session_exists(repo_root):
            try:
                existing = load_session(repo_root)
                # Session exists and is not expired
                raise SessionAlreadyActiveError(existing.get_expires_in_minutes())
            except SessionExpiredError:
                # Session expired, delete and continue
                delete_session(repo_root)

        # 3. Configure LLM if requested
        if llm or llm_provider:
            from preflights.application import configure_llm

            configure_llm(provider=llm_provider, strict_mode=llm_strict)

        # 4. Call Application API
        from preflights.application import get_llm_fallback_status, start_preflight

        result = start_preflight(intention, repo_root)

        # 5. Check for LLM fallback and warn user
        if (llm or llm_provider) and get_llm_fallback_status():
            print_llm_fallback_warning("credentials missing or provider error", json_output)

        # 6. Store session state
        state = _create_session_state(
            session_id=result.session_id,
            intention=intention,
            questions=result.questions,
        )
        save_session(repo_root, state)
        save_last_intention(repo_root, intention)

        # 5. Non-interactive mode: display and exit
        if non_interactive:
            print_start_success(state, json_output)
            return

        # 6. Interactive mode: display header and run loop
        click.echo(click.style(f'Starting preflight: "{intention}"', fg="green", bold=True))
        click.echo(f"Session expires in {SESSION_DURATION_MINUTES} minutes")

        _run_interactive_loop(repo_root, state)

    except CLIError as e:
        print_error(e, json_output)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        click.echo("")
        click.echo(click.style("Interrupted. Session saved.", fg="yellow"))
        click.echo("Use 'pf answer' to continue or 'pf reset' to cancel.")
        sys.exit(1)
    except Exception as e:
        print_app_error(
            "SYSTEM_ERROR",
            str(e),
            "Check logs or report issue",
            json_output,
        )
        sys.exit(ExitCode.SYSTEM_ERROR)


# =============================================================================
# preflights answer
# =============================================================================
@app.command()
@click.argument("answers", nargs=-1)
@click.option(
    "--answers-json",
    default=None,
    help="Provide answers as JSON inline",
)
@click.option(
    "--answers-file",
    default=None,
    type=click.Path(exists=True),
    help="Provide answers from JSON file",
)
@click.option(
    "--repo-path",
    default=None,
    help="Repository path (default: auto-discovery via .git)",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Continue in interactive mode after providing answers",
)
@click.option("--json", "json_output", is_flag=True, help="Output machine-readable JSON")
def answer(
    answers: tuple[str, ...],
    answers_json: str | None,
    answers_file: str | None,
    repo_path: str | None,
    interactive: bool,
    json_output: bool,
) -> None:
    """Provide answers to clarification questions.

    Format: key=value [key=value ...]

    Examples:
        pf answer auth_strategy=OAuth
        pf answer oauth_providers=Google,GitHub
        pf answer --answers-json '{"auth_strategy":"OAuth"}'
        pf answer auth_strategy=OAuth -i  # Continue interactively
    """
    try:
        # 0. Lazy cleanup of expired sessions (best effort)
        _lazy_cleanup_sessions()

        # 1. Discover repository root
        repo_root = get_repo_root(repo_path)

        # 2. Load session
        state = load_session(repo_root)

        # 3. Parse answers (precedence: file > json > args)
        answers_dict: dict[str, str | list[str]]
        if answers_file:
            with open(answers_file) as f:
                answers_dict = json.load(f)
        elif answers_json:
            answers_dict = json.loads(answers_json)
        else:
            answers_dict = parse_key_value_answers(answers)

        if not answers_dict:
            raise InvalidAnswerError("", "no answers provided")

        # 4. Local validation
        questions_by_id = {q.id: q for q in state.questions}
        validated_answers: dict[str, str | list[str]] = {}

        for qid, raw_answer in answers_dict.items():
            if qid not in questions_by_id:
                # Unknown question - pass through (may be new from clarification)
                validated_answers[qid] = raw_answer
            else:
                question = questions_by_id[qid]
                validated_answers[qid] = validate_answer(question, raw_answer)

        # 5. Update session answers
        state.answers.update(validated_answers)
        save_session(repo_root, state)

        # 6. Call Application API
        from preflights.application import continue_preflight

        result = continue_preflight(state.session_id, validated_answers)

        # 7. Handle result
        if result.status == "needs_more_answers":
            # Update questions in session
            if result.questions:
                new_questions = _questions_to_stored(result.questions)
                update_session_questions(repo_root, new_questions)
            state = load_session(repo_root)

            if interactive and not json_output:
                # Continue interactively
                _run_interactive_loop(repo_root, state)
            else:
                unanswered = [q for q in state.questions if q.id not in state.answers]
                print_needs_more_answers(unanswered, json_output)

        elif result.status == "needs_clarification":
            # Add new questions to session
            if result.questions:
                new_questions = _questions_to_stored(result.questions)
                update_session_questions(repo_root, new_questions)

            state = load_session(repo_root)

            if interactive and not json_output:
                # Continue interactively
                click.echo("")
                click.echo(click.style("Follow-up questions needed:", fg="yellow"))
                _run_interactive_loop(repo_root, state)
            else:
                print_needs_clarification(new_questions if result.questions else [], json_output)

        elif result.status == "completed":
            # Session complete, cleanup
            delete_session(repo_root)
            if result.artifacts:
                print_completed(
                    result.artifacts.task_path,
                    result.artifacts.adr_path,
                    result.artifacts.architecture_state_path,
                    result.artifacts.agent_prompt_path,
                    result.artifacts.agent_prompt,
                    json_output,
                )
            else:
                print_completed("docs/CURRENT_TASK.md", None, None, None, None, json_output)

        elif result.status == "error":
            if result.error:
                print_app_error(
                    result.error.code,
                    result.error.message,
                    result.error.recovery_hint,
                    json_output,
                )
                sys.exit(ExitCode.SYSTEM_ERROR)

    except CLIError as e:
        print_error(e, json_output)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        click.echo("")
        click.echo(click.style("Interrupted. Session saved.", fg="yellow"))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print_app_error(
            "PARSE_ERROR",
            f"Invalid JSON: {e}",
            "Check JSON syntax",
            json_output,
        )
        sys.exit(ExitCode.USER_ERROR)
    except Exception as e:
        print_app_error(
            "SYSTEM_ERROR",
            str(e),
            "Check logs or report issue",
            json_output,
        )
        sys.exit(ExitCode.SYSTEM_ERROR)


# =============================================================================
# preflights status
# =============================================================================
@app.command()
@click.option(
    "--repo-path",
    default=None,
    help="Repository path (default: auto-discovery via .git)",
)
@click.option("--json", "json_output", is_flag=True, help="Output machine-readable JSON")
def status(repo_path: str | None, json_output: bool) -> None:
    """Display current session state."""
    try:
        # 0. Lazy cleanup of expired sessions (best effort)
        _lazy_cleanup_sessions()

        # 1. Discover repository root
        repo_root = get_repo_root(repo_path)

        # 2. Load session
        state = load_session(repo_root)

        # 3. Display status
        print_status(state, json_output)

    except CLIError as e:
        print_error(e, json_output)
        sys.exit(e.exit_code)
    except Exception as e:
        print_app_error(
            "SYSTEM_ERROR",
            str(e),
            "Check logs or report issue",
            json_output,
        )
        sys.exit(ExitCode.SYSTEM_ERROR)


# =============================================================================
# preflights resume
# =============================================================================
@app.command()
@click.option(
    "--repo-path",
    default=None,
    help="Repository path (default: auto-discovery via .git)",
)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Show questions and exit (for scripts/CI)",
)
@click.option("--json", "json_output", is_flag=True, help="Output machine-readable JSON (implies --non-interactive)")
@click.option(
    "--llm",
    is_flag=True,
    help="Enable real LLM provider (requires API key in environment)",
)
@click.option(
    "--llm-strict",
    is_flag=True,
    help="Fail on LLM errors instead of falling back to mock",
)
@click.option(
    "--llm-provider",
    type=click.Choice(["anthropic", "openai", "openrouter"]),
    default=None,
    help="Override LLM provider (implies --llm)",
)
def resume(
    repo_path: str | None,
    non_interactive: bool,
    json_output: bool,
    llm: bool,
    llm_strict: bool,
    llm_provider: str | None,
) -> None:
    """Resume after session expiration or error.

    By default, runs in interactive mode.
    Use --llm to enable real LLM providers.
    """
    # --json implies non-interactive
    if json_output:
        non_interactive = True

    # --llm-provider implies --llm
    if llm_provider:
        llm = True

    try:
        # 0. Lazy cleanup of expired sessions (best effort)
        _lazy_cleanup_sessions()

        # 1. Discover repository root
        repo_root = get_repo_root(repo_path)

        # 2. Check for existing active session
        if session_exists(repo_root):
            try:
                existing = load_session(repo_root)
                # Session exists and is not expired
                raise SessionAlreadyActiveError(existing.get_expires_in_minutes())
            except SessionExpiredError:
                # Session expired, delete and continue
                delete_session(repo_root)

        # 3. Load last intention
        intention = load_last_intention(repo_root)

        # 4. Configure LLM if requested
        if llm or llm_provider:
            from preflights.application import configure_llm

            configure_llm(provider=llm_provider, strict_mode=llm_strict)

        # 5. Output resuming message
        if not json_output:
            click.echo(click.style(f'Resuming: "{intention}"', fg="green", bold=True))
            click.echo("")

        # 6. Call Application API
        from preflights.application import get_llm_fallback_status, start_preflight

        result = start_preflight(intention, repo_root)

        # 7. Check for LLM fallback and warn user
        if (llm or llm_provider) and get_llm_fallback_status():
            print_llm_fallback_warning("credentials missing or provider error", json_output)

        # 8. Store session state
        state = _create_session_state(
            session_id=result.session_id,
            intention=intention,
            questions=result.questions,
        )
        save_session(repo_root, state)

        # 9. Non-interactive mode: display and exit
        if non_interactive:
            print_start_success(state, json_output)
            return

        # 10. Interactive mode: run loop
        _run_interactive_loop(repo_root, state)

    except CLIError as e:
        print_error(e, json_output)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        click.echo("")
        click.echo(click.style("Interrupted. Session saved.", fg="yellow"))
        sys.exit(1)
    except Exception as e:
        print_app_error(
            "SYSTEM_ERROR",
            str(e),
            "Check logs or report issue",
            json_output,
        )
        sys.exit(ExitCode.SYSTEM_ERROR)


# =============================================================================
# preflights reset
# =============================================================================
@app.command()
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
@click.option(
    "--repo-path",
    default=None,
    help="Repository path (default: auto-discovery via .git)",
)
@click.option("--json", "json_output", is_flag=True, help="Output machine-readable JSON")
def reset(force: bool, repo_path: str | None, json_output: bool) -> None:
    """Cancel current session and cleanup."""
    try:
        # 0. Lazy cleanup of expired sessions (best effort)
        _lazy_cleanup_sessions()

        # 1. Discover repository root
        repo_root = get_repo_root(repo_path)

        # 2. Check for existing session
        if not session_exists(repo_root):
            raise NoActiveSessionError()

        # 3. Load session for display
        try:
            state = load_session(repo_root)
            intention = state.intention
        except SessionExpiredError:
            # Session expired but file exists
            intention = "(expired session)"

        # 4. Confirm (unless --force)
        if not force and not json_output:
            click.echo(f'⚠ This will cancel the current session: "{intention}"')
            click.echo("")
            if not click.confirm("Are you sure?", default=False):
                click.echo("Cancelled.")
                return

        # 5. Delete session
        delete_session(repo_root)

        # 6. Output
        if json_output:
            click.echo(json.dumps({"status": "reset"}, indent=2))
        else:
            click.echo("Session reset.")

    except CLIError as e:
        print_error(e, json_output)
        sys.exit(e.exit_code)
    except Exception as e:
        print_app_error(
            "SYSTEM_ERROR",
            str(e),
            "Check logs or report issue",
            json_output,
        )
        sys.exit(ExitCode.SYSTEM_ERROR)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
