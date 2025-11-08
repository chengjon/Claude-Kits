---
name: skill-template
description: Template for creating new Claude Code skills. Use when you need to create a modular, reusable skill that follows Claude Code best practices including the 500-line rule, progressive disclosure, and clear trigger keywords. Ideal for developers setting up new skills for code review, data analysis, documentation generation, testing automation, or any specialized development task.
---

# Skill Template

This is a template for creating a new skill in Claude Code that adheres to Anthropic's official best practices.

## When to Use This Template

Use this template when you need to:
- Create a new skill from scratch
- Follow the 500-line rule
- Implement progressive disclosure
- Set up proper YAML frontmatter
- Define clear skill activation triggers

## Steps to Create a New Skill

### 1. Copy this template directory

```bash
# Copy the entire skill-template directory to a new directory
cp -r skill-template my-new-skill

# Or use the skills manager
python scripts/skills_manager.py install my-new-skill --scope project
```

### 2. Edit YAML frontmatter

Open `SKILL.md` and update the frontmatter at the top:

```yaml
---
name: my-skill-name              # Lowercase, hyphens only (e.g., code-reviewer)
description: Detailed description of what this skill does and when to use it. Include ALL trigger keywords and phrases. This is crucial for Claude to discover when to use your skill.
allowed-tools: Read, Grep, Glob  # Optional: Restrict which tools Claude can use
---
```

**Important**: The `description` field is the ONLY way Claude discovers your skill. Claude uses natural language understanding to match user prompts with skill descriptions. There is no separate configuration file or rule engine.

**Tips for writing good descriptions**:
- Include what the skill does
- List when Claude should use it
- Add all relevant keywords and phrases
- Describe the use cases and scenarios
- Use 20-100 words (max 1024 characters)
- Be specific and actionable

**Good example**:
```yaml
description: Expert code review for quality, security, and maintainability. Use when reviewing code, checking pull requests, analyzing code quality, finding bugs, security vulnerabilities, or improving code structure. Ideal for pre-commit reviews, PR reviews, security audits, and refactoring guidance.
```

**Bad example** (too short, no keywords):
```yaml
description: Reviews code.
```

### 3. Write skill content (< 500 lines)

Structure your SKILL.md file:

```markdown
# My Skill Name

Brief introduction to what this skill does.

## When to Use This Skill

- Scenario 1
- Scenario 2
- Scenario 3

## Quick Start

Examples of how to invoke this skill:
> Example user prompt 1
> Example user prompt 2

## Main Content

[Your skill's core information, instructions, guidelines]

## Advanced Topics

For detailed information, see:
- [Topic 1](resources/topic-1.md)
- [Topic 2](resources/topic-2.md)
```

**Keep the main SKILL.md file under 500 lines!** If you exceed 500 lines, move detailed content to resource files.

### 4. Create resource files (optional but recommended)

If your skill requires detailed explanations:

```bash
mkdir -p my-new-skill/resources
```

Create focused Markdown files:
```
my-new-skill/
├── SKILL.md                      # < 500 lines - overview
└── resources/
    ├── advanced-usage.md         # < 500 lines each
    ├── troubleshooting.md
    └── examples.md
```

**Link to resources from SKILL.md**:
```markdown
For detailed configuration examples, see [resources/examples.md](resources/examples.md).
```

**Resource file best practices**:
- Each file should focus on a single topic
- Keep each file under 500 lines
- Use clear, descriptive filenames
- Add table of contents if > 100 lines
- Link back to main SKILL.md if needed

### 5. Optional: Restrict tools with allowed-tools

If your skill should only use specific tools, add to frontmatter:

```yaml
---
name: safe-file-reader
description: ...
allowed-tools: Read, Grep, Glob
---
```

This prevents Claude from using tools like `Bash` or `Edit` when this skill is active, improving safety.

**Common tool sets**:
- Read-only: `Read, Grep, Glob`
- Code analysis: `Read, Grep, Glob, Bash`
- Full access: (omit `allowed-tools` field)

### 6. Test your skill

#### Install the skill
```bash
# Personal scope (available to all your projects)
cp -r my-new-skill ~/.claude/skills/

# Project scope (only this project)
cp -r my-new-skill .claude/skills/
```

#### Test activation
Ask Claude questions that match your description keywords:

```
# If your description includes "code review"
> Review this code for security issues

# If your description includes "data analysis"
> Analyze the CSV file and find trends
```

#### Verify Claude uses your skill
Claude will typically mention when it's using a specific skill, or you can ask:
```
> Are you using any skills for this task?
```

### 7. Validate your skill

Use the validation tool to check compliance:

```bash
# Check YAML frontmatter, 500-line rule, etc.
python scripts/validate_skill.py my-new-skill/SKILL.md
```

## Example Skill Frontmatter

### Minimal (required fields only)
```yaml
---
name: my-skill
description: What this skill does and when to use it with relevant keywords.
---
```

### Full (with optional fields)
```yaml
---
name: code-reviewer
description: Expert code review for quality, security, and maintainability. Use when reviewing code, checking PRs, analyzing code quality, finding bugs, or improving maintainability.
allowed-tools: Read, Grep, Glob, Bash
---
```

## Best Practices Summary

✅ **DO**:
- Include detailed `description` with all trigger keywords
- Keep SKILL.md under 500 lines
- Use `resources/` for additional content
- Test with 3+ real scenarios before deploying
- Use `allowed-tools` for safety-critical skills
- Link resource files from main SKILL.md
- Iterate based on actual usage

❌ **DON'T**:
- Rely on external configuration files for activation
- Exceed 500 lines in main SKILL.md
- Write vague or short descriptions
- Forget to test skill activation
- Mix multiple unrelated topics in one skill

## Common Skill Types

### Code Quality Skills
- Code review
- Linting and formatting
- Refactoring guidance
- Test coverage analysis

### Development Workflow Skills
- Git workflow automation
- CI/CD assistance
- Documentation generation
- Dependency management

### Domain-Specific Skills
- Database query optimization
- API design review
- Security auditing
- Performance analysis

## Skill Activation Mechanism

**How Claude Code activates skills**:

Claude uses **natural language understanding** to match user prompts with skill descriptions. It analyzes:
- Keywords in the user's prompt
- Intent and context
- Current file types and project structure
- Semantic similarity between prompt and description

**NOT based on**:
- Rule engines or trigger configuration files
- Exact keyword matching
- Pattern matching systems
- External JSON configurations

This is why writing a comprehensive `description` field is crucial!

## Need Help?

- Check existing skills in `components/skills/` for examples
- Read the official Claude Code skills documentation
- Use the validation tool: `python scripts/validate_skill.py`
- Ask Claude for help: "How should I structure my skill?"

## Example Complete Skill Structure

```
code-reviewer/
├── SKILL.md                              # 450 lines
└── resources/
    ├── security-checklist.md             # 300 lines
    ├── performance-patterns.md           # 250 lines
    └── language-specific-rules.md        # 400 lines
```

**SKILL.md** provides overview and navigation, while **resources/** contain detailed topic-specific content that Claude loads progressively as needed.
