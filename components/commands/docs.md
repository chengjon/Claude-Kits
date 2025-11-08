---
description: Generate comprehensive documentation for code, APIs, or project components. Creates README files, API docs, function documentation, and usage guides with examples.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Documentation Generator Command

Generate clear, comprehensive documentation for your codebase.

## What You Should Do

1. **Analyze the code** to understand its purpose and functionality
2. **Identify what needs documentation**:
   - Public APIs and functions
   - Configuration options
   - Setup/installation steps
   - Usage examples
   - Architecture overview

3. **Generate appropriate documentation**:
   - **README.md** for project overview
   - **API.md** for API documentation
   - **Inline docs** (JSDoc, docstrings, etc.)
   - **CONTRIBUTING.md** for contributor guidelines

4. **Include practical examples** that users can copy and use

5. **Keep it user-focused**: Write for the intended audience (developers, end-users, etc.)

## Documentation Types

### Project README
Should include:
- **Project title and description**
- **Features** (bullet points)
- **Installation** instructions
- **Quick start** example
- **Configuration** options
- **Usage** examples
- **API reference** or link to docs
- **Contributing** guidelines
- **License**

### API Documentation
Should include:
- **Endpoint/function** description
- **Parameters** with types and descriptions
- **Return value** type and description
- **Examples** showing actual usage
- **Error cases** and how to handle them

### Function/Method Documentation
```javascript
/**
 * Calculates the total price including tax and discounts.
 *
 * @param {number} basePrice - The original price before any modifications
 * @param {number} taxRate - Tax rate as decimal (e.g., 0.08 for 8%)
 * @param {number} [discount=0] - Discount amount to subtract (optional)
 * @returns {number} The final price after tax and discount
 * @throws {Error} If basePrice or taxRate is negative
 *
 * @example
 * const total = calculateTotal(100, 0.08);
 * // Returns: 108
 *
 * @example
 * const total = calculateTotal(100, 0.08, 10);
 * // Returns: 97.2 (100 - 10 = 90, 90 * 1.08 = 97.2)
 */
function calculateTotal(basePrice, taxRate, discount = 0) {
  if (basePrice < 0 || taxRate < 0) {
    throw new Error('Price and tax rate must be non-negative');
  }
  return (basePrice - discount) * (1 + taxRate);
}
```

### Architecture Documentation
Should include:
- **System overview** diagram
- **Component descriptions**
- **Data flow** explanation
- **Key design decisions**
- **Technology stack**

## Output Format

### For README.md
```markdown
# Project Name

Brief description of what this project does.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

\`\`\`bash
npm install package-name
\`\`\`

## Quick Start

\`\`\`javascript
const lib = require('package-name');

// Basic usage example
const result = lib.doSomething();
\`\`\`

## Configuration

[Configuration options...]

## API Reference

[Link to detailed API docs or inline reference...]

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT
```

### For API Documentation
```markdown
## `functionName(param1, param2)`

Description of what this function does.

### Parameters

- `param1` (Type): Description
- `param2` (Type, optional): Description. Default: value

### Returns

(ReturnType): Description of return value

### Throws

- `ErrorType`: When this error occurs

### Example

\`\`\`language
const result = functionName(arg1, arg2);
console.log(result);
// Output: expected output
\`\`\`
```

## Best Practices

1. **Be concise but complete** - Cover everything needed, nothing more
2. **Use examples liberally** - Show don't just tell
3. **Keep it updated** - Documentation should match current code
4. **Write for your audience** - Technical level appropriate for users
5. **Include troubleshooting** - Common issues and solutions
6. **Link related docs** - Cross-reference for easy navigation

## Example Invocations

When user runs `/docs`, you should:
- Ask what needs documentation (if unclear)
- Analyze the relevant code
- Generate appropriate documentation
- Offer to create additional docs if needed

Be thorough and professional in all documentation you create.
