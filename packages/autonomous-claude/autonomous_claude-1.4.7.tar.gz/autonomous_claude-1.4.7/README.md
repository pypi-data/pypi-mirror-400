# autonomous-claude

Build apps autonomously with Claude Code CLI. Uses your existing Claude subscription - no API key required.

Based on [Anthropic's long-running agents guide](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## Installation

```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install autonomous-claude
uv tool install autonomous-claude
```

### Prerequisites

**Claude Code CLI**:
```bash
pnpm add -g @anthropic-ai/claude-code
claude login
```

**GitHub CLI** - required for issue tracking:
```bash
# Install: https://cli.github.com/
gh auth login
```

**Docker** - required for secure sandboxed execution:
```bash
# Install Docker: https://docs.docker.com/get-docker/
docker --version  # Verify installation
```

> By default, Claude runs in a Docker container with access only to your project directory. Use `--no-sandbox` to bypass this isolation (not recommended).

## Usage

```bash
# cd into your project directory first
cd my-project

# Start a new project or add features
autonomous-claude [INSTRUCTIONS]

# Continue work on existing features
autonomous-claude --continue

# Update to latest version
uv tool upgrade autonomous-claude
```

### Start a new project

```bash
# Create and enter project directory
mkdir notes-app && cd notes-app

# Interactive - prompts for description
autonomous-claude

# With description
autonomous-claude "An Apple Notes clone - local .md storage, folders, rich text, search"

# From a spec file
autonomous-claude ./app-spec.md
```

### Add features to an existing project

```bash
cd notes-app

# Add new features
autonomous-claude "Add dark mode and keyboard shortcuts"
```

> **Note:** If your project has open issues, you'll be asked to confirm. Use `--continue` to resume without adding new features.

### Continue work

Continue implementing existing features where you left off:

```bash
cd notes-app
autonomous-claude --continue
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--continue` | `-c` | Continue work on existing features | - |
| `--yes` | `-y` | Auto-accept spec (non-interactive mode) | false |
| `--no-sandbox` | — | Run without Docker sandbox (not recommended) | false |
| `--model` | `-m` | Claude model | Claude Code default |
| `--max-sessions` | `-n` | Max sessions (Claude Code invocations) | 100 |
| `--timeout` | `-t` | Timeout per session (seconds) | 18000 (5 hours) |

### Configuration

Create `~/.config/autonomous-claude/config.toml` to customize defaults:

```toml
[session]
timeout = 18000        # Seconds per session (default: 5 hours)
max_turns = 2000       # Max turns per Claude session
max_sessions = 100     # Max Claude sessions before stopping
spec_timeout = 600     # Timeout for spec generation (10 minutes)

[sandbox]
enabled = true         # Run in Docker sandbox (default: true)
memory_limit = "8g"    # Container memory limit
cpu_limit = 4.0        # Container CPU limit
```

### Spec Confirmation

Before building, Claude generates a detailed spec from your description. You can review and request changes:

```
Accept? [y] n
What needs changing? Add offline support and keyboard shortcuts
Updating spec...
```

Type `y` (or press Enter) to accept, or describe what to change.

### Project Files

The tool creates these files in your project:

| File | Purpose |
|------|---------|
| `.claude/CLAUDE.md` | Project specification (auto-loaded by Claude) |
| `.autonomous-claude/logs/` | Session logs (stdout, stderr, prompts) |
| `init.sh` | Dev environment setup script |
| `TODO.md` | Human tasks (API keys, credentials) - only if needed |

Features are tracked as **GitHub Issues** with the `autonomous-claude` label. View progress at `https://github.com/<owner>/<repo>/issues`.

## How It Works

### New projects
1. **Setup**: Creates a private GitHub repo (if needed)
2. **Session 1 (Initializer)**: Creates GitHub Issues for each testable feature
3. **Sessions 2+ (Coding Agent)**: Implements features one by one, closing issues when done

### Adding features to existing projects
1. **Session 1 (Enhancement Initializer)**: Creates new GitHub Issues for the requested features
2. **Sessions 2+ (Coding Agent)**: Implements the new features

Progress is tracked via GitHub Issues and git commits. Press `Ctrl+C` to stop, then `--continue` to resume.

## Example

```bash
$ mkdir apple-notes-clone && cd apple-notes-clone
$ autonomous-claude "An Apple Notes clone - web app with local .md file storage, folder organization, rich text editing, and full-text search"

╔═╗╦ ╦╔╦╗╔═╗╔╗╔╔═╗╔╦╗╔═╗╦ ╦╔═╗
╠═╣║ ║ ║ ║ ║║║║║ ║║║║║ ║║ ║╚═╗
╩ ╩╚═╝ ╩ ╚═╝╝╚╝╚═╝╩ ╩╚═╝╚═╝╚═╝
     Claude Code CLI

  Project     /home/user/apple-notes-clone
  Model       Claude Code default

Setting up new project...
...
```

## Security

### Docker Sandbox (Default)

By default, all Claude Code executions run inside an isolated Docker container.

**Mounts:**
| Host Path | Container Path | Mode | Why |
|-----------|---------------|------|-----|
| Project directory | `/workspace` | rw | Code being built |
| `~/.claude/.credentials.json` | `/home/node/.claude/.credentials.json` | rw | Auth tokens (needs write for refresh) |
| `~/.claude/settings.json` | `/home/node/.claude/settings.json` | ro | User preferences |
| `~/.claude/settings.local.json` | `/home/node/.claude/settings.local.json` | ro | Permission allowlists |
| `~/.claude/CLAUDE.md` | `/home/node/.claude/CLAUDE.md` | ro | Personal instructions |
| `~/.claude/skills/` | `/home/node/.claude/skills/` | rw | User-scoped skills (rw for deps/cache) |
| `~/.claude/plugins/` | `/home/node/.claude/plugins/` | ro | Installed plugins |
| `~/.config/gh` | `/home/node/.config/gh` | rw | GitHub CLI auth (rw for token refresh) |

Settings and plugins are read-only to prevent a sandboxed session from escalating permissions.

**Not accessible:** `~/.ssh`, `~/.aws`, or any directory outside your project.

**Limits:** 8GB RAM, 4 CPUs (configurable). Runs as non-root with all capabilities dropped.

## License

MIT - Based on [Anthropic's claude-quickstarts](https://github.com/anthropics/claude-quickstarts)
