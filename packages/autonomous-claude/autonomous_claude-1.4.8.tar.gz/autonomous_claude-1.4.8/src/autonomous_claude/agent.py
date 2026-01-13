import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from .client import ClaudeCLIClient
from .prompts import (
    get_initializer_prompt, get_coding_prompt,
    get_enhancement_initializer_prompt, write_spec_to_claude_md,
)
from . import ui
from .config import AUTONOMOUS_CLAUDE_DIR, LOGS_DIR


def run_with_spinner(func, *args, label: str = "Running...", **kwargs):
    result, error = [None], [None]

    def run():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=run)
    with ui.Spinner(label):
        thread.start()
        while thread.is_alive():
            thread.join(0.1)

    if error[0]:
        raise error[0]
    return result[0]


def get_actionable_issues(project_dir: Path) -> list[dict]:
    """Get open issues that the agent can work on (excludes 'needs-info' labeled issues)."""
    result = subprocess.run(
        ["gh", "issue", "list", "--state", "open", "--json", "number,title,body,labels"],
        capture_output=True, text=True, cwd=project_dir
    )
    if result.returncode != 0:
        return []
    try:
        issues = json.loads(result.stdout)
        # Filter out issues waiting for human response
        return [i for i in issues if not any(l.get("name") == "needs-info" for l in i.get("labels", []))]
    except json.JSONDecodeError:
        return []


def no_actionable_issues(project_dir: Path) -> bool:
    """Check if there are no actionable issues remaining (all closed or awaiting human response)."""
    return len(get_actionable_issues(project_dir)) == 0


def has_issue_history(project_dir: Path) -> bool:
    """Check if repo has ever had any issues (used to determine if this is a new project)."""
    result = subprocess.run(
        ["gh", "issue", "list", "--state", "all", "--json", "number", "--limit", "1"],
        capture_output=True, text=True, cwd=project_dir
    )
    if result.returncode != 0:
        return False
    try:
        return len(json.loads(result.stdout)) > 0
    except json.JSONDecodeError:
        return False


def write_session_log(path: Path, session_type: str, prompt: str, stdout: str, stderr: str, duration: float):
    with open(path, "w") as f:
        f.write(f"Type: {session_type}\nTime: {datetime.now().isoformat()}\nDuration: {duration:.1f}s\n")
        f.write(f"\n{'='*60}\nPROMPT:\n{'='*60}\n{prompt}\n")
        f.write(f"\n{'='*60}\nOUTPUT:\n{'='*60}\n{stdout or '(empty)'}\n")
        if stderr:
            f.write(f"\n{'='*60}\nSTDERR:\n{'='*60}\n{stderr}\n")


def run_session(project_dir: Path, model: str | None, prompt: str, timeout: int,
                session_type: str, spinner_label: str, sandbox: bool) -> float:
    logs_dir = project_dir / LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_type}.log"

    start = time.time()
    try:
        client = ClaudeCLIClient(project_dir=project_dir, model=model, timeout=timeout, sandbox=sandbox)
        stdout, stderr = run_with_spinner(client.query, prompt, label=spinner_label)
        duration = time.time() - start
        write_session_log(log_path, session_type, prompt, stdout, stderr, duration)
        ui.print_output(stdout, stderr)
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        write_session_log(log_path, session_type, prompt, "", f"TIMEOUT after {timeout}s", duration)
        ui.print_timeout(timeout, duration)
    except Exception as e:
        duration = time.time() - start
        write_session_log(log_path, session_type, prompt, "", str(e), duration)
        ui.print_error(e, duration, session_type)

    return duration


def run_agent_loop(
    project_dir: Path,
    model: str | None = None,
    max_sessions: int | None = None,
    app_spec: str | None = None,
    timeout: int = 1800,
    is_enhancement: bool = False,
    sandbox: bool = True,
    interactive: bool = True,
):
    project_dir.mkdir(parents=True, exist_ok=True)

    mcp_config = project_dir / ".mcp.json"
    if not mcp_config.exists():
        mcp_config.write_text('{"mcpServers": {}}\n')

    is_new_project = not has_issue_history(project_dir)
    ui.print_header(project_dir, model)

    needs_initializer = is_new_project
    needs_enhancement_init = is_enhancement

    if is_new_project:
        if app_spec:
            write_spec_to_claude_md(project_dir, app_spec)
        ui.print_new_project_notice()
    elif is_enhancement:
        if app_spec:
            write_spec_to_claude_md(project_dir, app_spec)
        ui.print_enhancement_notice()
    else:
        ui.print_resuming(project_dir)

    ui.print_separator()

    session_count = 0
    total_time = 0.0

    while True:
        if not needs_initializer and not needs_enhancement_init and no_actionable_issues(project_dir):
            break

        session_count += 1
        if max_sessions and session_count > max_sessions:
            ui.print_max_sessions(max_sessions)
            break

        issues_before = len(get_actionable_issues(project_dir))

        if needs_enhancement_init:
            prompt, session_type, label = get_enhancement_initializer_prompt(), "enhancement_init", "Enhancement init..."
            needs_enhancement_init = False
        elif needs_initializer:
            prompt, session_type, label = get_initializer_prompt(), "initializer", "Initializing..."
            needs_initializer = False
        else:
            prompt, session_type, label = get_coding_prompt(), "coding", "Coding..."

        print()
        duration = run_session(project_dir, model, prompt, timeout, session_type, label, sandbox)
        total_time += duration

        issues_after = len(get_actionable_issues(project_dir))
        issues_closed = issues_before - issues_after

        ui.print_issue_progress(project_dir, issues_closed, issues_after, duration, total_time)
        ui.print_separator()

        if no_actionable_issues(project_dir):
            break

        if interactive and ui.wait_for_stop_signal():
            ui.print_user_stopped()
            return

    ui.print_complete(project_dir, session_count, total_time)
