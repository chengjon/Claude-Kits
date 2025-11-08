#!/usr/bin/env bash

# This is a template for creating a new hook script in Claude Code.
# This template is for a UserPromptSubmit hook, which runs before Claude sees the user's prompt.

# Hook Input (from stdin):
# {
#   "session_id": "unique-session-id",
#   "prompt": "user's prompt",
#   "cwd": "/current/working/directory",
#   "permission_mode": "acceptEdits"
# }

# Hook Output (to stdout):
# Any text printed to stdout will be injected as context for Claude to see.
# For a UserPromptSubmit hook, this is typically a formatted message suggesting skills.

# Hook Exit Codes:
# 0: Success, continue normally
# 1: Error, stop and show error message
# 2: Block action (for PreToolUse hooks, not typically used for UserPromptSubmit)

set -e # Exit on any error

# Function to print formatted output
print_output() {
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "HOOK TEMPLATE OUTPUT"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "This is a template hook script."
  echo "It's meant to be customized for your specific needs."
  echo ""
  echo "Session ID: $SESSION_ID"
  echo "Prompt: $PROMPT"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main execution
main() {
  # Read input from stdin
  INPUT=$(cat)
  
  # Parse JSON input (requires jq to be installed)
  if command -v jq &> /dev/null; then
    SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')
    PROMPT=$(echo "$INPUT" | jq -r '.prompt')
  else
    # Fallback if jq is not available
    SESSION_ID="unknown"
    PROMPT="unknown"
  fi
  
  # Your hook logic goes here
  # For example, you could check the prompt for certain keywords
  # and suggest relevant skills or provide context.
  
  # For this template, we'll just print a generic message
  print_output
  
  # Exit with success code
  exit 0
}

# Run main function
main