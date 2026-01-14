#!/usr/bin/env bash
# Task-NG Installer
# Usage: curl -fsSL https://gitlab.com/mathias.ewald/task-ng/-/raw/main/scripts/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation paths
INSTALL_DIR="$HOME/.local/opt/task-ng"
BIN_DIR="$HOME/.local/bin"
VENV_DIR="$INSTALL_DIR/venv"

echo -e "${BLUE}Task-NG Installer${NC}"
echo "=================="
echo ""

# Check Python version
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}Error: Python 3 is required but not found${NC}"
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
  echo -e "${RED}Error: Python 3.11+ is required (found $PYTHON_VERSION)${NC}"
  exit 1
fi

echo -e "Found Python ${GREEN}$PYTHON_VERSION${NC}"

# Create directories
echo "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Check if already installed and capture current version
if [ -d "$VENV_DIR" ]; then
    echo -e "Updating existing installation..."
    if "$VENV_DIR/bin/task-ng" --version &>/dev/null; then
        OLD_VERSION=$("$VENV_DIR/bin/task-ng" --version 2>/dev/null | head -1)
        echo -e "Current version: ${BLUE}$OLD_VERSION${NC}"
    fi
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Install task-ng from GitLab
echo "Installing task-ng..."
"$VENV_DIR/bin/pip" install --upgrade pip -q

# Force reinstall task-ng to get latest git commit even if version unchanged
# Using --no-deps to avoid reinstalling all dependencies
"$VENV_DIR/bin/pip" install --force-reinstall --no-deps \
  "git+https://gitlab.com/mathias.ewald/task-ng.git" -q

# Ensure all dependencies are properly installed
"$VENV_DIR/bin/pip" install "git+https://gitlab.com/mathias.ewald/task-ng.git" -q

# Create symlink
echo "Creating symlink..."
ln -sf "$VENV_DIR/bin/task-ng" "$BIN_DIR/task-ng"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""

# Show installed version and upgrade status
NEW_VERSION=$("$VENV_DIR/bin/task-ng" --version 2>/dev/null | head -1)
if [ -n "$OLD_VERSION" ] && [ "$OLD_VERSION" != "$NEW_VERSION" ]; then
    echo -e "Upgraded: ${BLUE}$OLD_VERSION${NC} → ${GREEN}$NEW_VERSION${NC}"
else
    echo -e "Version: ${GREEN}$NEW_VERSION${NC}"
fi
echo ""
echo "Installed to: $INSTALL_DIR"
echo "Binary link:  $BIN_DIR/task-ng"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo -e "${YELLOW}Warning: ~/.local/bin is not in your PATH${NC}"
  echo ""
  echo "Add the following to your shell configuration file:"
  echo ""
  echo -e "${BLUE}For bash (~/.bashrc):${NC}"
  echo '  export PATH="$HOME/.local/bin:$PATH"'
  echo ""
  echo -e "${BLUE}For zsh (~/.zshrc):${NC}"
  echo '  export PATH="$HOME/.local/bin:$PATH"'
  echo ""
  echo -e "${BLUE}For fish (~/.config/fish/config.fish):${NC}"
  echo '  set -gx PATH $HOME/.local/bin $PATH'
  echo ""
  echo "Then restart your shell or run: source ~/.bashrc"
  echo ""
else
  echo "You can now run: task-ng --help"
fi
