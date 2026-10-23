# Markdown Standards

All Markdown files must comply with [Markdownlint](https://github.com/igorshubovych/markdownlint-cli)
rules as defined in `.markdownlintrc`.

## Configuration

A `.markdownlintrc` file is configured to enforce consistent Markdown
formatting:

```json
{
  "default": true,
  "MD013": {
    "tables": false,
    "code_blocks": false
  }
}
```

**Key Rules:**

- **MD001:** Heading levels must increment by one level at a time (h1 → h2 →
  h3, etc.)
- **MD013:** Line length must not exceed 80 characters (exceptions: tables and
  code blocks)
- **MD022:** Headings must be surrounded by blank lines
- **MD024:** No duplicate heading content (use unique or contextual names)
- **MD030:** List markers must be followed by exactly one space
- **MD031:** Fenced code blocks must be surrounded by blank lines
- **MD032:** Lists must be surrounded by blank lines
- **MD040:** Fenced code blocks must have a language specified
- **MD047:** Files must end with a single newline

## Automated Validation

Before committing changes, validate all Markdown files:

```bash
# Check all Markdown files for compliance
markdownlint --config .markdownlintrc "**/*.md"

# Automatically fix basic formatting issues
markdownlint --config .markdownlintrc --fix "**/*.md"
```

## Manual Guidelines

When creating or editing Markdown files:

1. **Line Length:** Break lines at 80 characters for readability (except in
   tables and code blocks which are exempt)
2. **Headings:** Use proper heading hierarchy and avoid duplicate titles
3. **Code Blocks:** Always specify the language (e.g., `bash`, `javascript`,
   `text`)
4. **Lists:** Ensure consistent spacing and indentation
5. **Links:** Keep URLs on the same line when possible; if too long, place on
   next line with proper indentation
6. **Tables & Diagrams:** These are exempt from line-length rules but must
   maintain structural integrity

### Examples

**Good - Proper line breaking:**

```markdown
This is a long description that exceeds 80 characters and is properly broken
into multiple lines for readability.
```

**Good - Code block with language:**

````markdown
```bash
task --list
```
````

**Good - Proper heading hierarchy:**

```markdown
# Main Title (h1)

## Section (h2)

### Subsection (h3)

- List item
```

**Bad - Heading level skip:**

```markdown
# Title
#### Subsection  # ❌ Should be ## first
```

**Bad - No language specified:**

````markdown
```
some code
```
````