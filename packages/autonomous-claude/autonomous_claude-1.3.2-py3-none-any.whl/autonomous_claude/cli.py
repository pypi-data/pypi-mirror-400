"""CLI for autonomous-claude."""

import json
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from . import __version__
from .agent import run_agent_loop
from .client import generate_app_spec, generate_task_spec, verify_claude_cli
from .config import get_config, SPEC_FILE, AUTONOMOUS_CLAUDE_DIR

console = Console()

# Legacy path for migration
LEGACY_FEATURES_FILE = f"{AUTONOMOUS_CLAUDE_DIR}/features.json"


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


def migrate_features_to_issues(project_dir: Path) -> bool:
    """Migrate legacy features.json to GitHub Issues. Returns True if migrated."""
    features_file = project_dir / LEGACY_FEATURES_FILE
    if not features_file.exists():
        return False

    # Check if repo exists
    repo = get_repo_remote(project_dir)
    if not repo:
        console.print("[yellow]Cannot migrate: no GitHub remote configured.[/yellow]")
        console.print("[dim]Set up a remote first: gh repo create[/dim]")
        return False

    console.print("[cyan]Migrating features.json to GitHub Issues...[/cyan]")

    try:
        features = json.loads(features_file.read_text())
    except json.JSONDecodeError as e:
        console.print(f"[red]Failed to parse features.json: {e}[/red]")
        return False

    # Ensure label exists
    subprocess.run(
        ["gh", "label", "create", "autonomous-claude",
         "--description", "Managed by autonomous-claude", "--force"],
        cwd=project_dir, capture_output=True
    )

    migrated = 0
    for f in features:
        if not f.get("passes"):
            description = f.get("description", "Untitled feature")
            steps = f.get("steps", [])
            body = "## Steps to verify\n" + "\n".join(f"- [ ] {s}" for s in steps) if steps else ""

            result = subprocess.run(
                ["gh", "issue", "create",
                 "--title", f"Feature: {description}",
                 "--body", body,
                 "--label", "autonomous-claude"],
                cwd=project_dir, capture_output=True, text=True
            )
            if result.returncode == 0:
                migrated += 1
                console.print(f"[dim]  Created: {result.stdout.strip()}[/dim]")

    # Backup old file
    features_file.rename(features_file.with_suffix(".json.migrated"))
    console.print(f"[green]Migrated {migrated} pending feature(s) to GitHub Issues[/green]")
    return True


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


def has_open_issues(project_dir: Path) -> tuple[bool, int]:
    """Check if project has open autonomous-claude issues. Returns (has_issues, count)."""
    result = subprocess.run(
        ["gh", "issue", "list", "--label", "autonomous-claude", "--state", "open", "--json", "number"],
        capture_output=True, text=True, cwd=project_dir
    )
    if result.returncode != 0:
        return False, 0
    try:
        issues = json.loads(result.stdout)
        return len(issues) > 0, len(issues)
    except json.JSONDecodeError:
        return False, 0


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
        verify_claude_cli()

    project_dir = Path.cwd()
    config = get_config()

    # Check for legacy features.json and migrate if needed
    legacy_file = project_dir / LEGACY_FEATURES_FILE
    if legacy_file.exists():
        migrate_features_to_issues(project_dir)

    # Check GitHub auth
    if not check_gh_auth():
        if not shutil.which("gh"):
            console.print("[red]GitHub CLI (gh) not installed.[/red]")
            console.print("[dim]Install: https://cli.github.com/[/dim]")
        else:
            console.print("[red]GitHub CLI not authenticated.[/red]")
            console.print("[dim]Run: gh auth login[/dim]")
        raise typer.Exit(1)

    # Check if project has open issues (enhancement mode)
    has_issues, issue_count = has_open_issues(project_dir)

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
        )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    instructions: str | None = typer.Argument(None, help="What to build or add"),
    continue_project: bool = typer.Option(False, "--continue", "-c", help="Continue existing features"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Auto-accept spec (non-interactive mode)"),
    no_sandbox: bool = typer.Option(False, "--no-sandbox", help="Run without Docker sandbox"),
    model: str | None = typer.Option(None, "--model", "-m", help="Claude model"),
    max_sessions: int | None = typer.Option(None, "--max-sessions", "-n", help="Max sessions"),
    timeout: int | None = typer.Option(None, "--timeout", "-t", help="Session timeout (seconds)"),
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"),
):
    """Build apps autonomously with Claude Code CLI."""
    if ctx.invoked_subcommand:
        return

    # Handle "update" passed as positional arg
    if instructions == "update":
        update()
        return

    sandbox = get_config().sandbox_enabled and not no_sandbox

    if continue_project:
        run_continue(model, max_sessions, timeout, sandbox, auto_accept=yes)
    else:
        run_default(instructions, model, max_sessions, timeout, sandbox, auto_accept=yes)


def run_continue(model: str | None, max_sessions: int | None, timeout: int | None, sandbox: bool = True, auto_accept: bool = False):
    """Continue work on existing features."""
    if not sandbox:
        verify_claude_cli()

    project_dir = Path.cwd()

    # Check for legacy features.json and migrate if needed
    legacy_file = project_dir / LEGACY_FEATURES_FILE
    if legacy_file.exists():
        migrate_features_to_issues(project_dir)

    # Check GitHub auth
    if not check_gh_auth():
        if not shutil.which("gh"):
            console.print("[red]GitHub CLI (gh) not installed.[/red]")
            console.print("[dim]Install: https://cli.github.com/[/dim]")
        else:
            console.print("[red]GitHub CLI not authenticated.[/red]")
            console.print("[dim]Run: gh auth login[/dim]")
        raise typer.Exit(1)

    # Check if there are open issues to work on
    has_issues, issue_count = has_open_issues(project_dir)
    if not has_issues:
        console.print("[yellow]No open issues to work on.[/yellow]")
        console.print("[dim]Run 'autonomous-claude \"description\"' to add new features.[/dim]")
        raise typer.Exit(0)

    console.print(f"[dim]Found {issue_count} open issue(s)[/dim]")

    spec = None
    if not (project_dir / SPEC_FILE).exists():
        console.print("[dim]No spec.md found.[/dim]")
        if auto_accept:
            console.print("[red]--yes with --continue requires existing spec.md[/red]")
            raise typer.Exit(1)
        description = typer.prompt("Briefly describe this project")
        console.print("[dim]Generating spec...[/dim]")
        spec = generate_app_spec(description, project_dir=project_dir)
        spec = confirm_spec(spec, title="App Spec", project_dir=project_dir, auto_accept=auto_accept)

    config = get_config()
    run_agent_loop(
        project_dir=project_dir.resolve(),
        model=model,
        max_sessions=max_sessions or config.max_sessions,
        app_spec=spec,
        timeout=timeout or config.timeout,
        sandbox=sandbox,
    )


@app.command()
def update():
    """Update to latest version from PyPI."""
    import urllib.request

    console.print(f"Current: {__version__}")
    console.print("Checking for updates...")

    with urllib.request.urlopen("https://pypi.org/pypi/autonomous-claude/json", timeout=10) as r:
        latest = json.loads(r.read().decode())["info"]["version"]

    current_base = __version__.split(".dev")[0].split("+")[0]
    if current_base == latest:
        console.print(f"Up to date ({latest})")
        return

    console.print(f"Updating {__version__} → {latest}...")
    result = subprocess.run(["uv", "tool", "install", "--force", "autonomous-claude"], capture_output=True, text=True)
    if result.returncode == 0:
        console.print(f"Updated to {latest}")
    else:
        console.print(f"[red]Update failed: {result.stderr}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
