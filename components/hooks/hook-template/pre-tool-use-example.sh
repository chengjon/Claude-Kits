#!/usr/bin/env bash

# PreToolUse Hook Example - Runs before a tool is invoked
# This example validates Bash commands before execution

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

# Only process Bash tool calls
if [ "$TOOL_NAME" != "Bash" ]; then
    exit 0
fi

# Extract command
COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command')

# Define blocked patterns
BLOCKED_PATTERNS=(
    "rm -rf /"
    "dd if=/dev/zero"
    ":(){ :|:& };:"
)

# Check for blocked patterns
for PATTERN in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qF "$PATTERN"; then
        echo "BLOCKED: Dangerous command detected: $PATTERN" >&2
        exit 2  # Exit code 2 blocks the tool call
    fi
done

# Log the command (append to file)
echo "[$(date)] $COMMAND" >> ~/.claude/bash-command-log.txt

# Exit 0 to allow the command
exit 0
