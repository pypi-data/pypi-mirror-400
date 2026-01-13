import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import __version__


def get_gh_token() -> str | None:
    """Get GitHub token from gh CLI (handles keyring-stored tokens)."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    # Fall back to environment variable
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

DEFAULT_IMAGE = "ghcr.io/ferdousbhai/autonomous-claude"


class DockerNotFoundError(RuntimeError):
    def __init__(self):
        super().__init__(
            "Docker is not installed.\n\n"
            "Install Docker:\n"
            "  https://docs.docker.com/get-docker/\n\n"
            "Or run without sandbox (not recommended):\n"
            "  autonomous-claude --no-sandbox"
        )


class DockerDaemonError(RuntimeError):
    def __init__(self, details: str = ""):
        msg = "Docker daemon is not running or inaccessible.\n\n"
        if "permission denied" in details.lower():
            msg += (
                "Permission denied. Try:\n"
                "  sudo usermod -aG docker $USER\n"
                "  # Then log out and back in\n\n"
            )
        msg += (
            "Start Docker:\n"
            "  sudo systemctl start docker  # Linux\n"
            "  open -a Docker               # macOS\n\n"
            "Or run without sandbox (not recommended):\n"
            "  autonomous-claude --no-sandbox"
        )
        super().__init__(msg)


class ImagePullError(RuntimeError):
    def __init__(self, image: str, details: str = ""):
        super().__init__(
            f"Failed to pull Docker image: {image}\n\n"
            f"Details: {details}\n\n"
            "Make sure you have internet access and the image exists."
        )


@dataclass
class SandboxConfig:
    memory_limit: str = "8g"
    cpu_limit: float = 4.0
    image: str = DEFAULT_IMAGE
    tag: str = field(default_factory=lambda: __version__.split('+')[0])


def is_docker_available() -> bool:
    return shutil.which("docker") is not None


def check_docker_daemon() -> tuple[bool, str]:
    if not is_docker_available():
        return False, "Docker not installed"
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
        return (True, "") if result.returncode == 0 else (False, result.stderr)
    except subprocess.TimeoutExpired:
        return False, "Docker daemon not responding"
    except Exception as e:
        return False, str(e)


def image_exists_locally(image: str, tag: str) -> bool:
    try:
        result = subprocess.run(["docker", "images", "-q", f"{image}:{tag}"],
                               capture_output=True, text=True, timeout=10)
        return bool(result.stdout.strip())
    except Exception:
        return False


def pull_image(image: str, tag: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(["docker", "pull", f"{image}:{tag}"],
                               capture_output=True, text=True, timeout=300)
        return (True, "") if result.returncode == 0 else (False, result.stderr)
    except subprocess.TimeoutExpired:
        return False, "Image pull timed out"
    except Exception as e:
        return False, str(e)


class DockerSandbox:
    def __init__(self, project_dir: Path, config: SandboxConfig | None = None):
        self.project_dir = project_dir.resolve()
        self.config = config or SandboxConfig()
        self.claude_dir = Path.home() / ".claude"
        self._verified = False
        self._active_tag = self.config.tag  # Track which tag we actually use

    def _verify_docker(self):
        if self._verified:
            return
        if not is_docker_available():
            raise DockerNotFoundError()
        ok, err = check_docker_daemon()
        if not ok:
            raise DockerDaemonError(err)
        self._verified = True

    def _ensure_image(self):
        image, tag = self.config.image, self.config.tag
        # Try requested tag first
        if image_exists_locally(image, tag):
            self._active_tag = tag
            return
        ok, err = pull_image(image, tag)
        if ok:
            self._active_tag = tag
            return
        # Fall back to latest (check local first, then pull)
        if tag != "latest":
            if image_exists_locally(image, "latest"):
                self._active_tag = "latest"
                return
            ok, _ = pull_image(image, "latest")
            if ok:
                self._active_tag = "latest"
                return
        raise ImagePullError(f"{image}:{tag}", err)

    def _build_command(self, claude_args: list[str]) -> list[str]:
        cmd = ["docker", "run", "--rm",
               f"--memory={self.config.memory_limit}",
               f"--cpus={self.config.cpu_limit}"]

        cmd.extend(["-v", f"{self.project_dir}:/workspace:rw"])

        mounts = [
            (".credentials.json", ".credentials.json", "rw"),
            ("settings.json", "settings.json", "ro"),
            ("settings.local.json", "settings.local.json", "ro"),
            ("CLAUDE.md", "CLAUDE.md", "ro"),
            ("skills", "skills", "rw"),
            ("plugins", "plugins", "ro"),
        ]
        for src, dest, mode in mounts:
            path = self.claude_dir / src
            if path.exists():
                cmd.extend(["-v", f"{path}:/home/node/.claude/{dest}:{mode}"])

        # Mount gh config as rw to allow token refresh
        gh_config = Path.home() / ".config" / "gh"
        if gh_config.exists():
            cmd.extend(["-v", f"{gh_config}:/home/node/.config/gh:rw"])

        # Pass GitHub token (handles keyring-stored tokens on host)
        gh_token = get_gh_token()
        if gh_token:
            cmd.extend(["-e", f"GH_TOKEN={gh_token}"])

        cmd.extend(["-w", "/workspace",
                    "-e", "HOME=/home/node",
                    "-e", "USER=node",
                    "--network", "bridge",
                    "--cap-drop=ALL",
                    "--security-opt=no-new-privileges",
                    f"{self.config.image}:{self._active_tag}"])
        cmd.extend(claude_args)
        return cmd

    def run(self, claude_args: list[str], timeout: int = 18000) -> tuple[str, str]:
        self._verify_docker()
        self._ensure_image()
        result = subprocess.run(self._build_command(claude_args),
                               capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr
