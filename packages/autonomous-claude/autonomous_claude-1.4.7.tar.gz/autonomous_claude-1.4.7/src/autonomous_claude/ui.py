"""UI components for autonomous-claude."""

import select
import sys
import termios
import time
import tty
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

console = Console()

LOGO = """[bold cyan]
╔═╗╦ ╦╔╦╗╔═╗╔╗╔╔═╗╔╦╗╔═╗╦ ╦╔═╗
╠═╣║ ║ ║ ║ ║║║║║ ║║║║║ ║║ ║╚═╗
╩ ╩╚═╝ ╩ ╚═╝╝╚╝╚═╝╩ ╩╚═╝╚═╝╚═╝
     [dim]Claude Code CLI[/dim][/bold cyan]
"""


def format_duration(s: float) -> str:
    if s < 60:
        return f"{s:.0f}s"
    m, s = int(s // 60), int(s % 60)
    if m < 60:
        return f"{m}m {s}s"
    return f"{m // 60}h {m % 60}m"


def play_notification() -> None:
    """Play terminal bell to notify user."""
    sys.stdout.write("\a")
    sys.stdout.flush()




def print_header(project_dir: Path, model: str | None) -> None:
    console.print(LOGO)
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column()
    table.add_row("Project", f"[bold]{project_dir}[/bold]")
    table.add_row("Model", model or "[dim]default[/dim]")
    console.print(table)
    console.print()


def print_new_project_notice() -> None:
    console.print("[yellow]Setting up new project...[/yellow]\n")


def print_enhancement_notice() -> None:
    console.print("[yellow]Adding features...[/yellow]\n")


def print_resuming(project_dir: Path) -> None:
    console.print("[green]Continuing...[/green]")


def print_issue_progress(project_dir: Path, issues_closed: int, open_count: int,
                         session_duration: float | None, total_time: float | None) -> None:
    """Print progress based on GitHub Issues."""
    console.print()

    if session_duration and total_time:
        console.print(f"[dim]Session: {format_duration(session_duration)} | Total: {format_duration(total_time)}[/dim]\n")

    if issues_closed > 0:
        console.print(f"[bold green]Closed {issues_closed} issue(s) this session[/bold green]")

    if open_count == 0:
        console.print("[bold green]All issues completed![/bold green]")
    else:
        style = "yellow" if open_count <= 3 else "white"
        console.print(f"[{style}]{open_count} issue(s) remaining[/{style}]")


def print_complete(project_dir: Path, sessions: int | None = None, total_time: float | None = None) -> None:
    console.print("\n[bold green]── COMPLETE ──[/bold green]\n")
    console.print("[green]All issues done![/green]")
    if sessions and total_time:
        console.print(f"[dim]{sessions} sessions | {format_duration(total_time)}[/dim]")
    console.print()


def print_output(stdout: str, stderr: str) -> None:
    if stdout:
        console.print(Panel(Markdown(stdout.strip()), title="[cyan]Claude[/cyan]", border_style="cyan", padding=(1, 2)))
    if stderr:
        console.print(f"[red][stderr]: {stderr}[/red]")


def print_separator() -> None:
    console.print("\n" + "─" * 70 + "\n")


def print_timeout(timeout: int, duration: float | None = None) -> None:
    console.print(f"[red]Timeout ({timeout}s, ran {format_duration(duration or 0)})[/red]")


def print_error(e: Exception, duration: float | None = None, session_type: str | None = None) -> None:
    console.print(f"[red]Error: {e}[/red]")
    if duration or session_type:
        parts = [f"Duration: {format_duration(duration)}" if duration else "", session_type or ""]
        console.print(f"[dim]{' | '.join(p for p in parts if p)}[/dim]")


def print_warning(msg: str) -> None:
    console.print(f"[yellow]Warning: {msg}[/yellow]")


def print_max_sessions(n: int) -> None:
    console.print(f"\n[yellow]Reached max sessions ({n})[/yellow]")


def print_user_stopped() -> None:
    console.print("[yellow]Stopped. Run 'autonomous-claude --continue' to resume.[/yellow]")


class Spinner:
    def __init__(self, label: str = "Running..."):
        self._label = label

    def __enter__(self):
        self._progress = Progress(
            SpinnerColumn(), TextColumn(f"[cyan]{self._label}[/cyan]"), TimeElapsedColumn(),
            console=console, transient=True
        )
        self._progress.start()
        self._progress.add_task("", total=None)
        return self

    def __exit__(self, *_):
        self._progress.stop()


def wait_for_stop_signal(timeout: float = 10.0) -> bool:
    """Wait for keypress. Returns True if user wants to stop."""
    play_notification()

    if not sys.stdin.isatty():
        return False

    old = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        start = time.time()
        remaining = timeout

        while remaining > 0:
            sys.stdout.write(f"\r\033[K  Press any key to stop, wait {remaining:.0f}s to continue... ")
            sys.stdout.flush()

            ready, _, _ = select.select([sys.stdin], [], [], min(1.0, remaining))
            if ready:
                sys.stdin.read(1)
                sys.stdout.write("\r\033[K")
                sys.stdout.flush()
                return True

            remaining = timeout - (time.time() - start)

        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
        return False
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
