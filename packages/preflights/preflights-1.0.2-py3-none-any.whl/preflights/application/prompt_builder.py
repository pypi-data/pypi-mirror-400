"""
Agent Prompt Builder.

Builds the AGENT_PROMPT.md content from Preflights artifacts.
This is Application layer responsibility (not Core).

The prompt prepares the optimal context for AI coding agents,
reducing friction between Preflights and agent startup.
"""

from __future__ import annotations

AGENT_PROMPT_PATH = "docs/AGENT_PROMPT.md"


def build_agent_prompt(
    *,
    task_path: str,
    adr_path: str | None,
    architecture_state_path: str | None,
) -> str:
    """
    Build the agent prompt content.

    The prompt follows a stable structure:
    1. Role definition
    2. Context (files to read)
    3. Strict rules
    4. Expected action

    Args:
        task_path: Relative path to CURRENT_TASK.md
        adr_path: Relative path to ADR file (if created)
        architecture_state_path: Relative path to ARCHITECTURE_STATE.md

    Returns:
        The complete prompt content as a string.
    """
    lines: list[str] = []

    # Header
    lines.append("# Agent Prompt")
    lines.append("")
    lines.append("Use this prompt to start your AI coding agent.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # The actual prompt (copyable block)
    lines.append("```")
    lines.append("You are a coding agent.")
    lines.append("")

    # Context - files to read
    lines.append("Read these files first:")
    if architecture_state_path:
        lines.append(f"- {architecture_state_path}")
    lines.append(f"- {task_path}")
    if adr_path:
        lines.append(f"- {adr_path}")
    lines.append("")

    # Strict rules
    lines.append("Rules:")
    lines.append("- Do NOT make architectural decisions beyond what is specified")
    lines.append("- Implement strictly what is described in the task")
    lines.append("- Follow the constraints and acceptance criteria exactly")
    lines.append("- If something is unclear or ambiguous, stop and ask")
    lines.append("- Stay within the allowed file paths (allowlist)")
    lines.append("")

    # Expected action
    lines.append("Start by reading the task file, then implement it step by step.")
    lines.append("```")
    lines.append("")

    # Instructions for the user
    lines.append("---")
    lines.append("")
    lines.append("**How to use:**")
    lines.append("")
    lines.append("Copy-paste the prompt above into your AI coding agent:")
    lines.append("- Claude Code: paste in terminal")
    lines.append("- Cursor: paste in chat")
    lines.append("- Windsurf: paste in chat")
    lines.append("- Other agents: paste in your agent's input")
    lines.append("")

    return "\n".join(lines)


def extract_prompt_content(full_prompt: str) -> str:
    """
    Extract just the copyable prompt from the full AGENT_PROMPT.md content.

    Returns the content between the ``` markers.
    """
    in_code_block = False
    prompt_lines: list[str] = []

    for line in full_prompt.split("\n"):
        if line.strip() == "```":
            if in_code_block:
                # End of code block
                break
            else:
                # Start of code block
                in_code_block = True
                continue

        if in_code_block:
            prompt_lines.append(line)

    return "\n".join(prompt_lines)
