#!/bin/sh
set -e

REPO_URL="https://ferdousbhai.com/releases/autonomous-claude"
VERSION="${VERSION:-latest}"

# Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS" in
  darwin) OS="darwin" ;;
  linux) OS="linux" ;;
  mingw*|msys*|cygwin*) OS="windows" ;;
  *) echo "Unsupported OS: $OS"; exit 1 ;;
esac

# Detect architecture
ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64) ARCH="amd64" ;;
  aarch64|arm64) ARCH="arm64" ;;
  *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

BINARY="autonomous-claude-${OS}-${ARCH}"
if [ "$OS" = "windows" ]; then
  BINARY="${BINARY}.exe"
fi

INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"

echo "Installing autonomous-claude ${VERSION}..."
echo "  OS: ${OS}"
echo "  Arch: ${ARCH}"
echo "  Install dir: ${INSTALL_DIR}"

mkdir -p "$INSTALL_DIR"

DOWNLOAD_URL="${REPO_URL}/${VERSION}/${BINARY}"
echo "Downloading from ${DOWNLOAD_URL}..."

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$DOWNLOAD_URL" -o "$INSTALL_DIR/autonomous-claude"
elif command -v wget >/dev/null 2>&1; then
  wget -q "$DOWNLOAD_URL" -O "$INSTALL_DIR/autonomous-claude"
else
  echo "Error: curl or wget required"
  exit 1
fi

chmod +x "$INSTALL_DIR/autonomous-claude"

echo ""
echo "autonomous-claude installed to $INSTALL_DIR/autonomous-claude"

# Check if in PATH
case ":$PATH:" in
  *":$INSTALL_DIR:"*) ;;
  *)
    echo ""
    echo "Add to your PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    ;;
esac

echo ""
echo "Run 'autonomous-claude --help' to get started"
