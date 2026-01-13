"""Interactive prompts for CLI.

Handles question display and answer collection in interactive mode.
"""

from __future__ import annotations

from typing import Any

import click

from preflights.cli.state import StoredQuestion

# Canonical value for "Other" option
OTHER_SPECIFY = "Other (specify)"


def display_question(question: StoredQuestion, number: int) -> None:
    """Display a single question with formatting."""
    click.echo("")
    click.echo(click.style(f"Q{number} [{question.id}]: {question.question}", bold=True))
    click.echo(f"   Type: {question.type}")

    if question.options:
        click.echo("   Options:")
        for i, opt in enumerate(question.options, 1):
            click.echo(f"      {i}. {opt}")

    if question.min_selections is not None or question.max_selections is not None:
        constraints = []
        if question.min_selections is not None:
            constraints.append(f"min: {question.min_selections}")
        if question.max_selections is not None:
            constraints.append(f"max: {question.max_selections}")
        click.echo(f"   ({', '.join(constraints)})")

    if question.optional:
        click.echo("   (optional - press Enter to skip)")


def prompt_free_text(question: StoredQuestion) -> str | None:
    """Prompt for free text input."""
    while True:
        raw_value: str = click.prompt(
            click.style(f"   {question.id}", fg="cyan"),
            default="",
            show_default=False,
        )
        value = raw_value.strip()

        if not value:
            if question.optional:
                return None
            click.echo(click.style("   Error: This field is required", fg="red"))
            continue

        return value


def prompt_single_choice(question: StoredQuestion) -> tuple[str, str | None]:
    """
    Prompt for single choice input.

    Returns:
        Tuple of (selected_option, other_value or None)
    """
    if not question.options:
        # Fallback to free text if no options
        value = prompt_free_text(question)
        return (value or "", None)

    options = list(question.options)
    options_lower = {opt.lower(): opt for opt in options}
    options_by_num = {str(i): opt for i, opt in enumerate(options, 1)}

    while True:
        value = click.prompt(
            click.style(f"   {question.id}", fg="cyan"),
            default="",
            show_default=False,
        )
        value = value.strip()

        if not value:
            if question.optional:
                return ("", None)
            click.echo(click.style("   Error: Please select an option", fg="red"))
            continue

        # Check if input is a number
        if value in options_by_num:
            selected = options_by_num[value]
        # Check if input matches an option (case-insensitive)
        elif value.lower() in options_lower:
            selected = options_lower[value.lower()]
        else:
            click.echo(
                click.style(f"   Error: Invalid option. Enter 1-{len(options)} or option text", fg="red")
            )
            continue

        # Handle "Other (specify)"
        other_value = None
        if selected == OTHER_SPECIFY:
            other_value = click.prompt(
                click.style("   Please specify", fg="cyan"),
                default="",
                show_default=False,
            ).strip()
            if not other_value:
                click.echo(click.style("   Error: Please provide a value for 'Other'", fg="red"))
                continue

        return (selected, other_value)


def prompt_multi_choice(question: StoredQuestion) -> tuple[list[str], str | None]:
    """
    Prompt for multi choice input.

    Returns:
        Tuple of (selected_options, other_value or None)
    """
    if not question.options:
        # Fallback to free text if no options
        value = prompt_free_text(question)
        return ([value] if value else [], None)

    options = list(question.options)
    options_lower = {opt.lower(): opt for opt in options}
    options_by_num = {str(i): opt for i, opt in enumerate(options, 1)}

    min_sel = question.min_selections or 0
    max_sel = question.max_selections

    hint = "Enter numbers or text separated by commas"
    if min_sel > 0:
        hint += f" (min: {min_sel})"
    if max_sel:
        hint += f" (max: {max_sel})"

    click.echo(click.style(f"   {hint}", dim=True))

    while True:
        value = click.prompt(
            click.style(f"   {question.id}", fg="cyan"),
            default="",
            show_default=False,
        )
        value = value.strip()

        if not value:
            if question.optional or min_sel == 0:
                return ([], None)
            click.echo(click.style(f"   Error: Please select at least {min_sel} option(s)", fg="red"))
            continue

        # Parse comma-separated values
        parts = [p.strip() for p in value.split(",") if p.strip()]
        selected: list[str] = []
        invalid = False

        for part in parts:
            # Check if input is a number
            if part in options_by_num:
                selected.append(options_by_num[part])
            # Check if input matches an option (case-insensitive)
            elif part.lower() in options_lower:
                selected.append(options_lower[part.lower()])
            else:
                click.echo(click.style(f"   Error: Invalid option '{part}'", fg="red"))
                invalid = True
                break

        if invalid:
            continue

        # Check constraints
        if len(selected) < min_sel:
            click.echo(click.style(f"   Error: Please select at least {min_sel} option(s)", fg="red"))
            continue

        if max_sel and len(selected) > max_sel:
            click.echo(click.style(f"   Error: Please select at most {max_sel} option(s)", fg="red"))
            continue

        # Handle "Other (specify)"
        other_value = None
        if OTHER_SPECIFY in selected:
            other_value = click.prompt(
                click.style("   Please specify 'Other'", fg="cyan"),
                default="",
                show_default=False,
            ).strip()
            if not other_value:
                click.echo(click.style("   Error: Please provide a value for 'Other'", fg="red"))
                continue

        return (selected, other_value)


def prompt_question(question: StoredQuestion, number: int) -> dict[str, str | list[str]]:
    """
    Prompt for a single question and return answers dict.

    Returns dict that may contain:
    - {question.id: answer} for regular answers
    - {question.id: answer, question.id + "__other": other_value} for "Other" selections
    """
    display_question(question, number)

    result: dict[str, str | list[str]] = {}

    if question.type == "free_text":
        value = prompt_free_text(question)
        if value is not None:
            result[question.id] = value

    elif question.type == "single_choice":
        selected, other_value = prompt_single_choice(question)
        if selected:
            result[question.id] = selected
            if other_value:
                result[f"{question.id}__other"] = other_value

    elif question.type == "multi_choice":
        selected_list, other_value = prompt_multi_choice(question)
        if selected_list:
            result[question.id] = selected_list
            if other_value:
                result[f"{question.id}__other"] = other_value

    else:
        # Unknown type, treat as free text
        value = prompt_free_text(question)
        if value is not None:
            result[question.id] = value

    return result


def prompt_all_questions(questions: list[StoredQuestion]) -> dict[str, str | list[str]]:
    """
    Prompt for all questions and return combined answers dict.

    Filters out conditional __other questions (they're handled inline).
    """
    all_answers: dict[str, str | list[str]] = {}

    # Filter out __other conditional questions
    visible_questions = [q for q in questions if q.depends_on_question_id is None]

    for i, question in enumerate(visible_questions, 1):
        answers = prompt_question(question, i)
        all_answers.update(answers)

    return all_answers


def confirm_answers(answers: dict[str, str | list[str]]) -> bool:
    """Show answers summary and confirm."""
    click.echo("")
    click.echo(click.style("Your answers:", bold=True))
    for key, value in answers.items():
        if isinstance(value, list):
            value_str = ", ".join(value)
        else:
            value_str = value
        click.echo(f"   {key} = {value_str}")

    click.echo("")
    return click.confirm("Submit these answers?", default=True)
