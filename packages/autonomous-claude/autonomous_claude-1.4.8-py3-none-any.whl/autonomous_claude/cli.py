"""CLI for autonomous-claude."""

import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from . import __version__
from .agent import run_agent_loop, get_actionable_issues
from .client import generate_app_spec, generate_task_spec, ensure_claude_cli
from .config import get_config

console = Console()

DEPRECATION_NOTICE = """
[yellow bold]DEPRECATION NOTICE[/yellow bold]

This Python version of autonomous-claude is deprecated.
Please switch to the new Go version:

  curl -fsSL https://ferdousbhai.com/install.sh | sh

The Go version is faster, has no dependencies, and will
receive all future updates. This Python version will no
longer be maintained.
"""


def show_deprecation_warning():
    """Show deprecation warning once per invocation."""
    console.print(Panel(DEPRECATION_NOTICE, border_style="yellow"))
    console.print()


def check_gh_auth() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    if not shutil.which("gh"):
        return False
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    return result.returncode == 0


def get_repo_remote(project_dir: Path) -> str | None:
    """Get the GitHub repo from git remote origin."""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True, text=True, cwd=project_dir
    )
    if result.returncode != 0:
        return None
    # Extract owner/repo from URL
    url = result.stdout.strip()
    # Handle both HTTPS and SSH URLs
    if "github.com" in url:
        # https://github.com/owner/repo.git or git@github.com:owner/repo.git
        parts = url.replace(":", "/").replace(".git", "").split("/")
        if len(parts) >= 2:
            return f"{parts[-2]}/{parts[-1]}"
    return None


def ensure_github_repo(project_dir: Path) -> str | None:
    """Ensure project has a GitHub repo. Returns repo name or None on failure."""
    # Check gh auth
    if not check_gh_auth():
        console.print("[red]GitHub CLI not authenticated.[/red]")
        console.print("[dim]Run: gh auth login[/dim]")
        return None

    # Check if already has remote
    existing = get_repo_remote(project_dir)
    if existing:
        console.print(f"[dim]Using repo:[/dim] {existing}")
        return existing

    # Need to create repo - check if git is initialized
    git_dir = project_dir / ".git"
    if not git_dir.exists():
        console.print("[dim]Initializing git...[/dim]")
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)

    # Create private repo (without --push since directory may be empty)
    repo_name = project_dir.name
    console.print(f"[dim]Creating private repo:[/dim] {repo_name}")
    result = subprocess.run(
        ["gh", "repo", "create", repo_name, "--private", "--source=."],
        cwd=project_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        console.print(f"[red]Failed to create repo:[/red] {result.stderr}")
        return None

    return get_repo_remote(project_dir)


def confirm_spec(spec: str, title: str = "Spec", project_dir: Path | None = None, auto_accept: bool = False) -> str:
    """Display spec for user confirmation or modification."""
    console.print()
    console.print(Panel(Markdown(spec), title=title, border_style="dim", padding=(1, 2)))

    if auto_accept:
        console.print("[dim]Auto-accepting spec (--yes)[/dim]")
        return spec

    while True:
        choice = typer.prompt("Accept?", default="y").lower().strip()
        if choice in ("y", "yes", ""):
            return spec
        feedback = choice if len(choice) > 1 else typer.prompt("What needs changing?")
        console.print("[dim]Updating spec...[/dim]")
        spec = generate_app_spec(f"{spec}\n\n## Changes Requested\n{feedback}", project_dir=project_dir)
        console.print()
        console.print(Panel(Markdown(spec), title=title, border_style="dim", padding=(1, 2)))


app = typer.Typer(
    name="autonomous-claude",
    help="Build apps autonomously with Claude Code CLI.",
    add_completion=False,
    no_args_is_help=False,
)


def version_callback(value: bool):
    if value:
        print(f"autonomous-claude {__version__}")
        raise typer.Exit()


def has_actionable_issues(project_dir: Path) -> tuple[bool, int]:
    """Check if project has issues the agent can work on. Returns (has_issues, count)."""
    issues = get_actionable_issues(project_dir)
    return len(issues) > 0, len(issues)


def require_gh_auth():
    """Ensure GitHub CLI is installed and authenticated. Exits on failure."""
    if not check_gh_auth():
        if not shutil.which("gh"):
            console.print("[red]GitHub CLI (gh) not installed.[/red]")
            console.print("[dim]Install: https://cli.github.com/[/dim]")
        else:
            console.print("[red]GitHub CLI not authenticated.[/red]")
            console.print("[dim]Run: gh auth login[/dim]")
        raise typer.Exit(1)


def run_default(
    instructions: str | None,
    model: str | None,
    max_sessions: int | None,
    timeout: int | None,
    sandbox: bool = True,
    auto_accept: bool = False,
):
    """Start new project or add features to existing one."""
    if not sandbox:
        ensure_claude_cli()

    project_dir = Path.cwd()
    config = get_config()
    require_gh_auth()

    # Check if project has actionable issues (enhancement mode)
    has_issues, issue_count = has_actionable_issues(project_dir)

    if has_issues:
        # Enhancement mode
        console.print(f"[yellow]Warning:[/yellow] {issue_count} open issue(s).")
        console.print("[dim]Use '--continue' to continue without adding new features.[/dim]")
        if not auto_accept and not typer.confirm("Proceed with adding new features?", default=False):
            raise typer.Exit(0)

        if not instructions:
            if auto_accept:
                console.print("[red]--yes requires instructions argument[/red]")
                raise typer.Exit(1)
            instructions = typer.prompt("What do you want to add")

        console.print(f"[dim]Adding to:[/dim] {project_dir}")
        console.print("[dim]Generating task spec...[/dim]")
        spec = generate_task_spec(instructions, project_dir=project_dir)
        spec = confirm_spec(spec, title="Task Spec", project_dir=project_dir, auto_accept=auto_accept)

        run_agent_loop(
            project_dir=project_dir.resolve(),
            model=model,
            max_sessions=max_sessions or config.max_sessions,
            app_spec=spec,
            timeout=timeout or config.timeout,
            is_enhancement=True,
            sandbox=sandbox,
            interactive=not auto_accept,
        )
    else:
        # New project mode
        if not instructions:
            if auto_accept:
                console.print("[red]--yes requires instructions argument[/red]")
                raise typer.Exit(1)
            instructions = typer.prompt("Describe what you want to build")

        # Check if instructions is a file path
        try:
            spec_path = Path(instructions)
            is_file = spec_path.exists() and spec_path.is_file()
        except OSError:
            is_file = False

        if is_file:
            console.print(f"[dim]Reading spec from:[/dim] {spec_path}")
            spec = spec_path.read_text()
        else:
            console.print("[dim]Generating spec...[/dim]")
            spec = generate_app_spec(instructions, project_dir=project_dir)

        spec = confirm_spec(spec, title="App Spec", project_dir=project_dir, auto_accept=auto_accept)

        # Ensure GitHub repo exists for new projects
        repo = ensure_github_repo(project_dir)
        if not repo:
            console.print("[red]Cannot proceed without GitHub repo.[/red]")
            raise typer.Exit(1)

        run_agent_loop(
            project_dir=project_dir.resolve(),
            model=model,
            max_sessions=max_sessions or config.max_sessions,
            app_spec=spec,
            timeout=timeout or config.timeout,
            sandbox=sandbox,
            interactive=not auto_accept,
        )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    instructions: str | None = typer.Argument(None, help="What to build or add"),
    continue_project: bool = typer.Option(False, "--continue", "-c", help="Continue existing features"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Non-interactive mode (no prompts, auto-accept)"),
    no_sandbox: bool = typer.Option(False, "--no-sandbox", help="Run without Docker sandbox"),
    model: str | None = typer.Option(None, "--model", "-m", help="Claude model"),
    max_sessions: int | None = typer.Option(None, "--max-sessions", "-n", help="Max sessions"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Session timeout (seconds)"),
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"),
):
    """Build apps autonomously with Claude Code CLI."""
    if ctx.invoked_subcommand:
        return

    # Show deprecation warning
    show_deprecation_warning()

    sandbox = get_config().sandbox_enabled and not no_sandbox

    if continue_project:
        run_continue(model, max_sessions, timeout, sandbox, auto_accept=yes)
    else:
        run_default(instructions, model, max_sessions, timeout, sandbox, auto_accept=yes)


def run_continue(model: str | None, max_sessions: int | None, timeout: int | None, sandbox: bool = True, auto_accept: bool = False):
    """Continue work on existing features."""
    if not sandbox:
        ensure_claude_cli()

    project_dir = Path.cwd()
    require_gh_auth()

    # Check if there are actionable issues to work on
    has_issues, issue_count = has_actionable_issues(project_dir)
    if not has_issues:
        console.print("[yellow]No open issues to work on.[/yellow]")
        console.print("[dim]Run 'autonomous-claude \"description\"' to add new features.[/dim]")
        raise typer.Exit(0)

    console.print(f"[dim]Found {issue_count} open issue(s)[/dim]")

    config = get_config()
    run_agent_loop(
        project_dir=project_dir.resolve(),
        model=model,
        max_sessions=max_sessions or config.max_sessions,
        timeout=timeout or config.timeout,
        sandbox=sandbox,
        interactive=not auto_accept,
    )


if __name__ == "__main__":
    app()
