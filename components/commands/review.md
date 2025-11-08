---
description: Perform a comprehensive code review of recent changes, checking for bugs, security issues, performance problems, and best practices. Reviews git diff or staged changes.
allowed-tools: Read, Grep, Glob, Bash
---

# Code Review Command

Perform a thorough code review of recent changes in the repository.

## What You Should Do

1. **Get the changes** - Run `git diff` or `git diff --cached` to see what changed
2. **Analyze each file** systematically for:
   - **Security vulnerabilities** (SQL injection, XSS, auth bypass, etc.)
   - **Logic errors** and potential bugs
   - **Performance issues** (N+1 queries, inefficient algorithms)
   - **Code quality** (naming, structure, duplication)
   - **Best practices** violations
   - **Missing error handling**
   - **Test coverage** gaps

3. **Provide structured feedback** organized by severity:
   - 🔴 **CRITICAL**: Security vulnerabilities, data loss risks, logic errors
   - 🟡 **WARNINGS**: Performance issues, missing error handling
   - 🟢 **SUGGESTIONS**: Code style, refactoring opportunities

4. **Include specific locations** with file paths and line numbers

5. **Provide fix examples** with before/after code

## Review Checklist

### Security
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Proper input validation
- [ ] Authentication/authorization checks
- [ ] No exposed secrets or API keys
- [ ] Secure password handling

### Logic & Bugs
- [ ] No off-by-one errors
- [ ] Null/undefined handling
- [ ] Edge cases covered
- [ ] Async code handled correctly
- [ ] Race conditions prevented

### Performance
- [ ] No N+1 database queries
- [ ] Proper indexing
- [ ] Efficient algorithms
- [ ] Resource cleanup
- [ ] Caching where appropriate

### Code Quality
- [ ] Clear naming
- [ ] No code duplication
- [ ] Proper error handling
- [ ] Meaningful comments
- [ ] Tests included

## Output Format

```markdown
# Code Review Results

## Summary
Reviewed X files with Y lines changed (+A, -B)
Found: N critical issues, M warnings, K suggestions

## 🔴 CRITICAL: [Issue Title]

**Location**: `path/to/file.ext:42`
**Issue**: [Description]

**Current Code**:
\`\`\`language
[problematic code]
\`\`\`

**Fixed Code**:
\`\`\`language
[corrected code]
\`\`\`

**Impact**: [Why this matters]

---

[Repeat for each issue...]
```

Focus on being constructive and educational in your feedback.
