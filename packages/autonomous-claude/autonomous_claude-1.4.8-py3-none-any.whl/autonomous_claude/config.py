import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

CONFIG_FILE = Path.home() / ".config" / "autonomous-claude" / "config.toml"
AUTONOMOUS_CLAUDE_DIR = ".autonomous-claude"
CLAUDE_MD_FILE = ".claude/CLAUDE.md"
LOGS_DIR = f"{AUTONOMOUS_CLAUDE_DIR}/logs"
SANDBOX_IMAGE = "ghcr.io/ferdousbhai/autonomous-claude"


@dataclass
class Config:
    timeout: int = 18000
    max_turns: int = 2000
    max_sessions: int = 100
    spec_timeout: int = 1800
    sandbox_enabled: bool = True
    sandbox_memory_limit: str = "8g"
    sandbox_cpu_limit: float = 4.0
    sandbox_image: str = SANDBOX_IMAGE
    sandbox_tag: str = ""

    @classmethod
    def load(cls) -> "Config":
        config = cls()
        if not CONFIG_FILE.exists() or not tomllib:
            return config

        try:
            data = tomllib.loads(CONFIG_FILE.read_text())
        except Exception:
            return config

        mappings = {
            "session": ["timeout", "max_turns", "max_sessions", "spec_timeout"],
            "sandbox": {"enabled": "sandbox_enabled", "memory_limit": "sandbox_memory_limit",
                       "cpu_limit": "sandbox_cpu_limit", "image": "sandbox_image", "tag": "sandbox_tag"},
        }

        for section, fields in mappings.items():
            if section not in data:
                continue
            if isinstance(fields, list):
                for f in fields:
                    if f in data[section]:
                        setattr(config, f, data[section][f])
            else:
                for file_key, attr in fields.items():
                    if file_key in data[section]:
                        setattr(config, attr, data[section][file_key])

        return config


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.load()
    return _config
