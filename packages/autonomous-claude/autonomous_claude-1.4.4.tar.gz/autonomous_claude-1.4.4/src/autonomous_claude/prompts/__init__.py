"""Prompt loading and generation."""

from importlib import resources
from pathlib import Path

from ..config import CLAUDE_MD_FILE


def _load_bundled_prompt(name: str) -> str:
    with resources.files("autonomous_claude.prompts").joinpath(f"{name}.md").open() as f:
        return f.read()


def get_initializer_prompt() -> str:
    return _load_bundled_prompt("initializer_prompt")


def get_coding_prompt() -> str:
    return _load_bundled_prompt("coding_prompt")


def get_adoption_initializer_prompt() -> str:
    return _load_bundled_prompt("adoption_initializer_prompt")


def get_enhancement_initializer_prompt() -> str:
    return _load_bundled_prompt("enhancement_initializer_prompt")


def write_spec_to_claude_md(project_dir: Path, spec_content: str) -> None:
    """Write spec content to .claude/CLAUDE.md, appending if file exists."""
    claude_md = project_dir / CLAUDE_MD_FILE
    claude_md.parent.mkdir(parents=True, exist_ok=True)

    if claude_md.exists():
        existing = claude_md.read_text()
        # Append new spec under a clear section header
        claude_md.write_text(f"{existing}\n\n---\n\n## New Requirements\n\n{spec_content}")
    else:
        claude_md.write_text(spec_content)
