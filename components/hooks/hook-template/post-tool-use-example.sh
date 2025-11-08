#!/usr/bin/env bash

# PostToolUse Hook Example - Runs after a tool successfully completes
# This example logs file changes and can provide feedback to Claude

set -e

# Read input from stdin
INPUT=$(cat)

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi

# Parse input JSON
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input')
TOOL_RESPONSE=$(echo "$INPUT" | jq -r '.tool_response')

# Example: Log file edits
if [ "$TOOL_NAME" == "Edit" ] || [ "$TOOL_NAME" == "Write" ]; then
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path')
    echo "[$(date)] $TOOL_NAME: $FILE_PATH" >> ~/.claude/file-changes-log.txt
fi

# Example: Run linter after code changes
if [ "$TOOL_NAME" == "Write" ] && [[ "$FILE_PATH" == *.py ]]; then
    # Optional: Run Python linter (uncomment if you want this)
    # python -m flake8 "$FILE_PATH" 2>&1 || true
    :
fi

# Exit 0 to continue normally
exit 0
