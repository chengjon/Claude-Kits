---
allowed-tools: Read, Write, Bash, Edit
argument-hint: [component-name] [--option value]
description: Template for creating custom slash commands with examples and best practices
model: claude-sonnet-4-5-20250929
---

# Command Template

This template demonstrates how to create custom slash commands in Claude Code with proper frontmatter configuration.

## What This Command Does

[Describe the command's purpose clearly and concisely]

Example:
> This command creates a new React component with proper structure, tests, and documentation.

## Frontmatter Configuration

The frontmatter at the top of this file configures the command's behavior:

```yaml
---
allowed-tools: Read, Write, Bash, Edit  # Tools this command can use
argument-hint: [arg1] [arg2] [--flag]   # Shows in autocomplete
description: Brief description          # Shows in /help menu
model: claude-sonnet-4-5-20250929      # Model to use (optional)
disable-model-invocation: false         # Prevent SlashCommand tool from calling this
---
```

### Frontmatter Fields Explained

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `allowed-tools` | No | Restrict which tools Claude can use | `Read, Bash(git:*)` |
| `argument-hint` | No | Show expected arguments in autocomplete | `[name] [type]` |
| `description` | Recommended | Show in /help, used by SlashCommand tool | `Create a component` |
| `model` | No | Override model for this command | `claude-3-5-haiku-20241022` |
| `disable-model-invocation` | No | Prevent SlashCommand tool from calling this | `true` |

## Command Content

After the frontmatter, write clear instructions for Claude:

### 1. Describe What to Do

Use imperative statements:
- "Create a new file at..."
- "Run the following commands..."
- "Analyze the code and..."

### 2. Use Parameters

Access command arguments:
- `$ARGUMENTS` - All arguments as one string
- `$1`, `$2`, `$3` - Individual positional arguments

Example:
```markdown
Create a component named $1 of type $2 in the directory $3.
```

### 3. Execute Bash Commands

Use `!` prefix to run commands and include output:
```markdown
Current directory structure: !`ls -la`
Git status: !`git status --short`
```

### 4. Reference Files

Use `@` prefix to include file contents:
```markdown
Use the same style as @src/components/Button.tsx
Follow patterns from @docs/component-guidelines.md
```

## Complete Example: Git Commit Command

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
description: Create a git commit with staged changes
model: claude-3-5-haiku-20241022
---

# Git Commit Command

## Context

Current git status: !`git status`
Staged changes: !`git diff --cached`
Recent commits: !`git log --oneline -5`

## Your Task

Create a git commit with the following message: $ARGUMENTS

Before committing:
1. Verify staged changes are correct
2. Ensure the message follows conventional commit format
3. Add co-authored-by footer

Run:
```bash
git commit -m "$(cat <<'EOF'
$ARGUMENTS

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

After committing, show the result with `git log -1`.
```

## Example Commands by Use Case

### Code Generation
```markdown
---
description: Generate a React component with tests
argument-hint: [component-name]
---

Create a new React component named $1 with:
- TypeScript interface
- Jest tests
- Storybook stories
```

### Code Review
```markdown
---
description: Review code for security issues
allowed-tools: Read, Grep
---

Analyze recent changes and check for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Exposed secrets or API keys
```

### Refactoring
```markdown
---
description: Extract repeated code into utility functions
allowed-tools: Read, Edit, Grep
---

Find duplicated code patterns and extract them to utilities.
```

### Documentation
```markdown
---
description: Generate API documentation from code
allowed-tools: Read, Write, Grep
---

Create API docs for all exported functions in: $ARGUMENTS
```

## Using Arguments

### All Arguments ($ARGUMENTS)
```markdown
---
argument-hint: [commit message]
---

Create commit with message: $ARGUMENTS
# Example usage: /commit fix: resolve login bug
# $ARGUMENTS becomes: "fix: resolve login bug"
```

### Individual Arguments ($1, $2, $3)
```markdown
---
argument-hint: [name] [type] [path]
---

Create component $1 of type $2 in directory $3
# Example usage: /create Button functional src/components
# $1 = "Button", $2 = "functional", $3 = "src/components"
```

## Tool Restrictions

### Allow Specific Commands
```yaml
---
allowed-tools: Bash(git add:*), Bash(git commit:*), Read
---
```

### Allow Broad Access
```yaml
---
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---
```

### Inherit All Tools
```yaml
---
# Omit allowed-tools field to inherit from conversation
---
```

## Best Practices

1. **Write Clear Descriptions**
   - Include trigger keywords
   - Explain what the command does
   - Keep under 100 words

2. **Use Argument Hints**
   - Show expected parameter format
   - Use brackets for required: `[name]`
   - Use square brackets for optional: `[--flag value]`

3. **Restrict Tools When Appropriate**
   - Use `allowed-tools` for safety-critical commands
   - Allow only necessary Bash patterns
   - Example: `Bash(git:*)` for git-only commands

4. **Test Your Commands**
   ```bash
   # Install to project
   cp my-command.md .claude/commands/

   # Test it
   claude
   > /my-command arg1 arg2
   ```

5. **Organize with Subdirectories**
   ```
   .claude/commands/
   ├── frontend/
   │   └── component.md
   ├── backend/
   │   └── endpoint.md
   └── git/
       └── commit.md
   ```

## Limitations

- Commands are text-based prompts, not executable scripts
- Complex logic should be in Skills or Agents instead
- Cannot maintain state between invocations
- SlashCommand tool has 15,000 character budget for all commands

## When to Use Commands vs Skills

**Use Slash Commands for:**
- Quick, frequently-used prompts
- Simple task templates
- Commands you invoke explicitly
- Single-file content

**Use Skills for:**
- Complex workflows with multiple steps
- Functionality Claude should discover automatically
- Multi-file documentation and resources
- Team-wide standardized processes

## Example Command Files

### Example 1: Review PR
```markdown
---
allowed-tools: Bash(git:*), Read, Grep
argument-hint: [pr-number]
description: Review pull request for quality and security
---

Review PR #$1

Steps:
1. Fetch PR: !`gh pr checkout $1`
2. Get changes: !`git diff main...HEAD`
3. Analyze for security, performance, and best practices
4. Provide prioritized feedback
```

### Example 2: Run Tests
```markdown
---
allowed-tools: Bash(npm test:*)
argument-hint: [test-pattern]
description: Run tests matching a pattern
---

Run tests matching: $ARGUMENTS

Command: !`npm test -- $ARGUMENTS`

Analyze failures and suggest fixes.
```

### Example 3: Generate Docs
```markdown
---
allowed-tools: Read, Write, Grep
argument-hint: [file-path]
description: Generate documentation from code comments
---

Generate docs for: $ARGUMENTS

1. Read file: @$ARGUMENTS
2. Extract JSDoc comments
3. Create markdown documentation
4. Save to docs/$ARGUMENTS.md
```

## Installation

### Personal Commands (all projects)
```bash
cp my-command.md ~/.claude/commands/
```

### Project Commands (this project only)
```bash
cp my-command.md .claude/commands/
```

### Organized by Category
```bash
mkdir -p .claude/commands/git
cp commit.md .claude/commands/git/
```

## See Also

- [Slash Commands Documentation](/zh-CN/docs/claude-code/slash-commands)
- [Skills Documentation](/zh-CN/docs/claude-code/skills)
- [Sub-agents Documentation](/zh-CN/docs/claude-code/sub-agents)
