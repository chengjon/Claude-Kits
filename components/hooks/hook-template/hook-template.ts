#!/usr/bin/env node

// This is a template for creating a new hook script in Claude Code.
// This template is for a UserPromptSubmit hook, which runs before Claude sees the user's prompt.

// Hook Input (from stdin):
// {
//   "session_id": "unique-session-id",
//   "prompt": "user's prompt",
//   "cwd": "/current/working/directory",
//   "permission_mode": "acceptEdits"
// }

// Hook Output (to stdout):
// Any text printed to stdout will be injected as context for Claude to see.
// For a UserPromptSubmit hook, this is typically a formatted message suggesting skills.

// Hook Exit Codes:
// 0: Success, continue normally
// 1: Error, stop and show error message
// 2: Block action (for PreToolUse hooks, not typically used for UserPromptSubmit)

import { readFileSync } from 'fs';

interface HookInput {
  session_id: string;
  prompt: string;
  cwd: string;
  permission_mode: string;
}

async function main() {
  try {
    // Read input from stdin
    const input = readFileSync(0, 'utf-8');
    const data: HookInput = JSON.parse(input);
    
    const sessionId = data.session_id;
    const prompt = data.prompt;
    
    // Your hook logic goes here
    // For example, you could check the prompt for certain keywords
    // and suggest relevant skills or provide context.
    
    // For this template, we'll just print a generic message
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('HOOK TEMPLATE OUTPUT');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('');
    console.log('This is a template hook script.');
    console.log('It\'s meant to be customized for your specific needs.');
    console.log('');
    console.log(`Session ID: ${sessionId}`);
    console.log(`Prompt: ${prompt}`);
    console.log('');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    // Exit with success code
    process.exit(0);
  } catch (err) {
    console.error('Error in hook template:', err);
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Uncaught error:', err);
  process.exit(1);
});