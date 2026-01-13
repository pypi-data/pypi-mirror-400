"""Prompt loading and generation."""

from importlib import resources
from pathlib import Path

from ..config import CLAUDE_MD_FILE


def _load_prompt(name: str) -> str:
    with resources.files("autonomous_claude.prompts").joinpath(f"{name}.md").open() as f:
        return f.read()


def get_initializer_prompt() -> str:
    template = _load_prompt("setup_prompt")
    return template.format(
        mode="INITIALIZER",
        context="setting up a new project for autonomous development",
        understand_extra="",
        issue_scope="testable feature (scale complexity appropriately, create issues for ALL planned features)",
        extra_tasks="\n4. **Create `init.sh`** - install deps, start dev server\n\n5. **Create project structure** - based on tech stack\n\n",
        commit_msg="Initial setup",
    )


def get_enhancement_initializer_prompt() -> str:
    template = _load_prompt("setup_prompt")
    return template.format(
        mode="ENHANCEMENT",
        context="adding features to an existing project",
        understand_extra=" and review existing issues:\n   ```bash\n   gh issue list --state all\n   ```",
        issue_scope="new feature",
        extra_tasks="",
        commit_msg="Add new feature issues",
    )


def get_coding_prompt() -> str:
    return _load_prompt("coding_prompt")


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
