"""Output formatting for CLI."""

from __future__ import annotations

import json
import sys
from typing import Any

import click

from preflights.cli.errors import CLIError
from preflights.cli.state import SessionState, StoredQuestion

# Canonical value for "Other" option
OTHER_SPECIFY = "Other (specify)"


def is_conditional_question(q: StoredQuestion) -> bool:
    """Check if question is a conditional __other field."""
    return q.depends_on_question_id is not None


def format_questions_human(questions: list[StoredQuestion], prefix: str = "Q") -> str:
    """Format questions for human-readable output."""
    lines: list[str] = []
    q_num = 0

    for q in questions:
        # Hide __other conditional questions
        if is_conditional_question(q):
            continue

        q_num += 1
        lines.append(f"{prefix}{q_num} [{q.id}]: {q.question}")
        lines.append(f"   Type: {q.type}")

        if q.options:
            # Filter out __other questions from options display
            display_options = [opt for opt in q.options]
            lines.append(f"   Options: {', '.join(display_options)}")

        if q.min_selections is not None or q.max_selections is not None:
            constraints = []
            if q.min_selections is not None:
                constraints.append(f"Min: {q.min_selections}")
            if q.max_selections is not None:
                constraints.append(f"Max: {q.max_selections}")
            else:
                constraints.append("Max: none")
            lines.append(f"   {', '.join(constraints)}")

        if q.optional:
            lines.append("   (optional)")

        lines.append("")

    return "\n".join(lines)


def format_questions_json(questions: list[StoredQuestion]) -> list[dict[str, Any]]:
    """Format questions for JSON output."""
    result = []
    for q in questions:
        item: dict[str, Any] = {
            "id": q.id,
            "type": q.type,
            "question": q.question,
            "optional": q.optional,
        }
        if q.options:
            item["options"] = list(q.options)
        if q.min_selections is not None:
            item["min_selections"] = q.min_selections
        if q.max_selections is not None:
            item["max_selections"] = q.max_selections
        if q.depends_on_question_id:
            item["depends_on_question_id"] = q.depends_on_question_id
            item["depends_on_value"] = q.depends_on_value
        result.append(item)
    return result


def print_start_success(
    state: SessionState,
    json_output: bool = False,
) -> None:
    """Print start command success output."""
    if json_output:
        output = {
            "status": "started",
            "session_id": state.session_id,
            "expires_at": state.expires_at,
            "questions": format_questions_json(state.questions),
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo("Session started (expires in 30m)")
        click.echo("")
        click.echo("Questions to answer:")
        click.echo("")
        click.echo(format_questions_human(state.questions))
        click.echo("Use: preflights answer <key>=<value> ...")


def print_needs_more_answers(
    questions: list[StoredQuestion],
    json_output: bool = False,
) -> None:
    """Print needs_more_answers status."""
    if json_output:
        output = {
            "status": "needs_more_answers",
            "questions": format_questions_json(questions),
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo("Remaining questions:")
        click.echo("")
        click.echo(format_questions_human(questions))
        # Suggest command
        visible = [q for q in questions if not is_conditional_question(q)]
        if visible:
            q = visible[0]
            if q.options:
                click.echo(f"Use: preflights answer {q.id}={q.options[0]}")
            else:
                click.echo(f"Use: preflights answer {q.id}=<value>")


def print_needs_clarification(
    questions: list[StoredQuestion],
    json_output: bool = False,
) -> None:
    """Print needs_clarification status."""
    if json_output:
        output = {
            "status": "needs_clarification",
            "questions": format_questions_json(questions),
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo("Follow-up questions needed:")
        click.echo("")
        click.echo(format_questions_human(questions))
        # Suggest command
        visible = [q for q in questions if not is_conditional_question(q)]
        if visible:
            q = visible[0]
            if q.options:
                click.echo(f"Use: preflights answer {q.id}={q.options[0]}")
            else:
                click.echo(f"Use: preflights answer {q.id}=<value>")


def print_completed(
    task_path: str,
    adr_path: str | None,
    architecture_state_path: str | None,
    agent_prompt_path: str | None = None,
    agent_prompt: str | None = None,
    json_output: bool = False,
) -> None:
    """Print completed status."""
    if json_output:
        artifacts: dict[str, str] = {"task": task_path}
        if adr_path:
            artifacts["adr"] = adr_path
        if architecture_state_path:
            artifacts["architecture_state"] = architecture_state_path
        if agent_prompt_path:
            artifacts["agent_prompt"] = agent_prompt_path

        output: dict[str, Any] = {
            "status": "completed",
            "artifacts": artifacts,
        }
        if agent_prompt:
            output["agent_prompt"] = agent_prompt

        click.echo(json.dumps(output, indent=2))
    else:
        click.echo(click.style("\u2714 Preflight completed", fg="green"))
        click.echo("")
        click.echo("Artifacts created:")
        if adr_path:
            click.echo(f"  ADR:    {adr_path}")
        click.echo(f"  Task:   {task_path}")
        if architecture_state_path:
            click.echo(f"  State:  {architecture_state_path}")
        if agent_prompt_path:
            click.echo(f"  Prompt: {agent_prompt_path}")
        click.echo("")

        # Display the agent prompt with clear instructions
        if agent_prompt:
            click.echo(click.style("=" * 60, fg="cyan"))
            click.echo(click.style("NEXT STEP - START YOUR CODING AGENT", fg="cyan", bold=True))
            click.echo(click.style("=" * 60, fg="cyan"))
            click.echo("")
            click.echo(agent_prompt)
            click.echo(click.style("-" * 60, fg="cyan"))
            click.echo("Copy-paste the prompt above into Claude Code, Cursor, or Windsurf.")
            click.echo(f"Prompt also saved to: {agent_prompt_path}")
            click.echo("")

        click.echo("Session closed.")


def print_status(
    state: SessionState,
    json_output: bool = False,
) -> None:
    """Print session status."""
    if json_output:
        questions_status = []
        for q in state.questions:
            if is_conditional_question(q):
                continue
            item: dict[str, Any] = {
                "id": q.id,
                "answered": q.id in state.answers,
            }
            if q.id in state.answers:
                item["value"] = state.answers[q.id]
            else:
                item["question"] = q.question
                if q.options:
                    item["options"] = list(q.options)
            questions_status.append(item)

        output = {
            "status": "active",
            "intention": state.intention,
            "expires_at": state.expires_at,
            "questions": questions_status,
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo(f'Active session: "{state.intention}"')
        click.echo(f"Expires: {state.expires_at} (in {state.get_expires_in_minutes()} minutes)")
        click.echo("")
        click.echo("Questions:")

        pending_questions = []
        for q in state.questions:
            if is_conditional_question(q):
                continue
            if q.id in state.answers:
                value = state.answers[q.id]
                if isinstance(value, list):
                    value = ", ".join(value)
                click.echo(f"  \u2714 [{q.id}] = {value}")
            else:
                click.echo(f"  \u23f3 [{q.id}] (pending)")
                pending_questions.append(q)

        if pending_questions:
            click.echo("")
            # Suggest next command
            q = pending_questions[0]
            if q.options:
                click.echo(f"Next: preflights answer {q.id}={q.options[0]}")
            else:
                click.echo(f"Next: preflights answer {q.id}=<value>")


def print_error(
    error: CLIError,
    json_output: bool = False,
) -> None:
    """Print error message."""
    if json_output:
        error_dict: dict[str, Any] = {
            "code": error.code,
            "message": error.message,
        }
        if error.hint:
            error_dict["recovery_hint"] = error.hint
        output = {
            "status": "error",
            "error": error_dict,
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo(click.style(f"\u2717 Error: {error.code}", fg="red"), err=True)
        click.echo(f"  {error.message}", err=True)
        if error.hint:
            click.echo("", err=True)
            click.echo(f"\U0001f4a1 Hint: {error.hint}", err=True)


def print_app_error(
    code: str,
    message: str,
    hint: str | None,
    json_output: bool = False,
) -> None:
    """Print application error (from PreflightsApp)."""
    if json_output:
        output: dict[str, Any] = {
            "status": "error",
            "error": {
                "code": code,
                "message": message,
            },
        }
        if hint:
            output["error"]["recovery_hint"] = hint
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo(click.style(f"\u2717 Error: {code}", fg="red"), err=True)
        click.echo(f"  {message}", err=True)
        if hint:
            click.echo("", err=True)
            click.echo(f"\U0001f4a1 Hint: {hint}", err=True)
