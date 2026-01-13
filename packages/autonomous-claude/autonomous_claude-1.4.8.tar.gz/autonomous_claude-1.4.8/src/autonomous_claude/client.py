import shutil
import subprocess
from pathlib import Path

from .config import get_config
from .sandbox import DockerSandbox, SandboxConfig, is_docker_available, check_docker_daemon


def ensure_claude_cli():
    if not shutil.which("claude"):
        raise RuntimeError(
            "Claude Code CLI not found.\n\n"
            "Install: npm install -g @anthropic-ai/claude-code\n"
            "Then run: claude"
        )


SPEC_TEMPLATES = {
    "app": {
        "prompt": '''Write a concise application specification for: "{description}"
{context_hint}
Format:
# <App Name>

## Overview
One paragraph.

## Core Features
- Feature 1: Brief description
(3-6 features)

## Tech Stack
Appropriate technologies.

Output only the spec.''',
        "fallback": "# Application\n\n## Overview\n{description}",
    },
    "task": {
        "prompt": '''Write a concise task specification for: "{description}"
{context_hint}
Format:
# Task: <Brief Title>

## Overview
One paragraph.

## Requirements
- Key requirements

## Guidelines
- Follow existing patterns

Output only the spec.''',
        "fallback": "# Task\n\n## Overview\n{description}",
    },
}


def generate_spec(description: str, spec_type: str = "app", project_dir: Path | None = None) -> str:
    """Generate a spec using Claude. spec_type can be 'app' or 'task'."""
    ensure_claude_cli()
    config = get_config()
    template = SPEC_TEMPLATES[spec_type]

    context_hint = "\n\nCheck for *.md files that might contain relevant context." if project_dir else ""
    prompt = template["prompt"].format(description=description, context_hint=context_hint)

    cmd = ["claude", "--print", "-p", prompt]
    if project_dir:
        cmd.extend(["--dangerously-skip-permissions", "--allowedTools", "Read,Glob"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.spec_timeout,
                           cwd=str(project_dir) if project_dir else None)
    return result.stdout.strip() or template["fallback"].format(description=description)


def generate_app_spec(description: str, project_dir: Path | None = None) -> str:
    return generate_spec(description, "app", project_dir)


def generate_task_spec(task: str, project_dir: Path | None = None) -> str:
    return generate_spec(task, "task", project_dir)


class ClaudeCLIClient:
    def __init__(
        self,
        project_dir: Path,
        model: str | None = None,
        timeout: int | None = None,
        sandbox: bool = True,
    ):
        config = get_config()
        self.project_dir = project_dir.resolve()
        self.model = model
        self.max_turns = config.max_turns
        self.timeout = timeout or config.timeout
        self.sandbox = sandbox and config.sandbox_enabled
        self._sandbox_client = None

        if self.sandbox:
            if not is_docker_available():
                raise RuntimeError("Docker required for sandbox. Install Docker or use --no-sandbox")

            ok, err = check_docker_daemon()
            if not ok:
                raise RuntimeError(f"Docker daemon not running: {err}")

            from . import __version__
            tag = config.sandbox_tag or __version__.split('+')[0]

            self._sandbox_client = DockerSandbox(
                project_dir=self.project_dir,
                config=SandboxConfig(
                    memory_limit=config.sandbox_memory_limit,
                    cpu_limit=config.sandbox_cpu_limit,
                    image=config.sandbox_image,
                    tag=tag,
                ),
            )
        else:
            ensure_claude_cli()

    def _build_args(self, prompt: str) -> list[str]:
        args = ["--print", "--dangerously-skip-permissions", "-p", prompt, "--max-turns", str(self.max_turns)]
        if self.model:
            args.extend(["--model", self.model])
        return args

    def query(self, prompt: str) -> tuple[str, str]:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        args = self._build_args(prompt)

        if self._sandbox_client:
            return self._sandbox_client.run(args, timeout=self.timeout)

        result = subprocess.run(["claude"] + args, cwd=str(self.project_dir),
                               capture_output=True, text=True, timeout=self.timeout)
        return result.stdout, result.stderr
