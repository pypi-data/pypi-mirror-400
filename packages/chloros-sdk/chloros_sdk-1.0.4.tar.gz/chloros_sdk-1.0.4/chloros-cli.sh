#!/bin/bash
# Chloros CLI Launcher for Linux
# This script launches the Chloros command-line interface
# Mirrors the functionality of Chloros_CLI.bat on Windows

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for virtual environment
VENV_PATH="$HOME/.chloros-venv"
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
fi

# Check if chloros_cli.py exists
if [ ! -f "$SCRIPT_DIR/chloros_cli.py" ]; then
    echo "Error: chloros_cli.py not found in $SCRIPT_DIR"
    exit 1
fi

# Run the CLI
python3 "$SCRIPT_DIR/chloros_cli.py" "$@"
