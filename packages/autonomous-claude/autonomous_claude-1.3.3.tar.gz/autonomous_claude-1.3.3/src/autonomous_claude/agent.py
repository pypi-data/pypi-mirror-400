import json
import shutil
import subprocess
import threading
import time
from datetime import datetime
from importlib import resources
from pathlib import Path

from .client import ClaudeCLIClient
from .prompts import (
    get_initializer_prompt, get_coding_prompt,
    get_adoption_initializer_prompt, get_enhancement_initializer_prompt,
    copy_spec_to_project,
)
from . import ui
from .config import AUTONOMOUS_CLAUDE_DIR, LOGS_DIR, get_config

SKILLS_DIR = Path.home() / ".claude" / "skills"
RALPH_STATE_FILE = f"{AUTONOMOUS_CLAUDE_DIR}/.ralph-state"


def install_bundled_skills():
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    with resources.as_file(resources.files("autonomous_claude") / "skills") as src:
        if not src.exists():
            return
        for skill in src.iterdir():
            if not skill.is_dir():
                continue
            dest = SKILLS_DIR / skill.name
            if dest.exists():
                continue
            shutil.copytree(skill, dest)
            if skill.name == "playwright-skill" and (dest / "package.json").exists():
                subprocess.run(["pnpm", "run", "setup"], cwd=dest, capture_output=True)


def setup_ralph_hook(project_dir: Path):
    config = get_config()
    if not config.ralph_enabled:
        return

    hooks_dir = project_dir / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    with resources.as_file(resources.files("autonomous_claude") / "hooks" / "stop_hook.sh") as src:
        if src.exists():
            dest = hooks_dir / "stop_hook.sh"
            shutil.copy(src, dest)
            dest.chmod(0o755)

    settings_file = project_dir / ".claude" / "settings.local.json"
    settings = {}
    if settings_file.exists():
        try:
            settings = json.loads(settings_file.read_text())
        except json.JSONDecodeError:
            pass

    settings["hooks"] = {
        "Stop": [{
            "matcher": "*",
            "hooks": [{
                "type": "command",
                "command": f"RALPH_MAX_ITERATIONS={config.ralph_max_iterations} .claude/hooks/stop_hook.sh"
            }]
        }]
    }
    settings_file.write_text(json.dumps(settings, indent=2))


def reset_ralph_state(project_dir: Path):
    state_file = project_dir / RALPH_STATE_FILE
    if state_file.exists():
        state_file.unlink()


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


def get_open_issues(project_dir: Path) -> list[dict]:
    result = subprocess.run(
        ["gh", "issue", "list", "--label", "autonomous-claude", "--state", "open", "--json", "number,title,body"],
        capture_output=True, text=True, cwd=project_dir
    )
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def all_issues_closed(project_dir: Path) -> bool:
    return len(get_open_issues(project_dir)) == 0


def has_existing_issues(project_dir: Path) -> bool:
    result = subprocess.run(
        ["gh", "issue", "list", "--label", "autonomous-claude", "--state", "all", "--json", "number", "--limit", "1"],
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
    is_adoption: bool = False,
    is_enhancement: bool = False,
    sandbox: bool = True,
    interactive: bool = True,
):
    project_dir.mkdir(parents=True, exist_ok=True)

    mcp_config = project_dir / ".mcp.json"
    if not mcp_config.exists():
        mcp_config.write_text('{"mcpServers": {}}\n')

    is_new_project = not has_existing_issues(project_dir)
    if is_new_project:
        run_with_spinner(install_bundled_skills, label="Installing skills...")

    setup_ralph_hook(project_dir)
    ui.print_header(project_dir, model)

    needs_initializer = is_new_project
    needs_enhancement_init = is_enhancement

    if is_new_project:
        if app_spec:
            copy_spec_to_project(project_dir, app_spec)
        ui.print_adoption_notice() if is_adoption else ui.print_new_project_notice()
    elif is_enhancement:
        if app_spec:
            copy_spec_to_project(project_dir, app_spec)
        ui.print_enhancement_notice()
    else:
        ui.print_resuming(project_dir)

    ui.print_separator()

    session_count = 0
    total_time = 0.0

    while True:
        if not needs_initializer and not needs_enhancement_init and all_issues_closed(project_dir):
            break

        session_count += 1
        if max_sessions and session_count > max_sessions:
            ui.print_max_sessions(max_sessions)
            break

        issues_before = len(get_open_issues(project_dir))

        if needs_enhancement_init:
            prompt, session_type, label = get_enhancement_initializer_prompt(), "enhancement_init", "Enhancement init..."
            needs_enhancement_init = False
        elif needs_initializer:
            if is_adoption:
                prompt, session_type, label = get_adoption_initializer_prompt(), "adoption_init", "Adoption init..."
            else:
                prompt, session_type, label = get_initializer_prompt(), "initializer", "Initializing..."
            needs_initializer = False
        else:
            prompt, session_type, label = get_coding_prompt(), "coding", "Coding..."

        reset_ralph_state(project_dir)

        print()
        duration = run_session(project_dir, model, prompt, timeout, session_type, label, sandbox)
        total_time += duration

        issues_after = len(get_open_issues(project_dir))
        issues_closed = issues_before - issues_after

        ui.print_issue_progress(project_dir, issues_closed, issues_after, duration, total_time)
        ui.print_separator()

        if all_issues_closed(project_dir):
            break

        if interactive and ui.wait_for_stop_signal():
            ui.print_user_stopped()
            return

    ui.print_complete(project_dir, session_count, total_time)
