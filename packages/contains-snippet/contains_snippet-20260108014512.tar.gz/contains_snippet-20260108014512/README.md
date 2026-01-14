# contains-snippet

A command-line tool that checks whether a given snippet exists anywhere within
a file. For plain text files (like `.md`), it searches the raw content
directly. For source code files (`.py`, `.yml`, `.yaml`), it checks for the
snippet rendered as comments.

## Installation

```bash
pip install -e .
```

## Usage

```bash
contains-snippet --snippet-file SNIPPET_FILE FILE [FILE ...]
```

### Exit Codes

- `0` - All files contain the snippet
- `1` - One or more files are missing the snippet
- `2` - Usage/configuration/runtime error

### Matching Rules (Default)

- `.md` files: Raw substring match
- `.py`, `.yml`, `.yaml` files: Commented match (lines prefixed with `#`)
- Other extensions: Raw substring match

### Examples

Check if a license notice appears in a README:

```bash
contains-snippet --snippet-file license_notice.txt README.md
```

Check if a header comment exists in multiple Python files:

```bash
contains-snippet --snippet-file header.txt src/*.py
```

### Configuring Match Behavior

#### Force Commented Matching: `--comment-prefix`

Force all files to use commented matching with a specific prefix:

```bash
# Check JavaScript files with // comments
contains-snippet --snippet-file header.txt --comment-prefix "//" src/*.js

# Force .md files to match as comments (not raw)
contains-snippet --snippet-file notice.txt --comment-prefix "#" docs/*.md
```

#### Infer from Extension: `--infer-comment-prefix`

Enable extension-based inference using built-in mapping:

| Extension | Match Type |
|-----------|------------|
| .md       | raw        |
| .py       | # comments |
| .yml      | # comments |
| .yaml     | # comments |
| (other)   | raw        |

```bash
contains-snippet --snippet-file header.txt --infer-comment-prefix src/*.py docs/*.md
```

#### Custom Extension Mapping: `--comment-prefix-map`

Override or extend the built-in mapping (requires `--infer-comment-prefix`):

```bash
# Add JavaScript and TypeScript support
contains-snippet --snippet-file header.txt \
  --infer-comment-prefix \
  --comment-prefix-map ".js=//,.ts=//" \
  src/*

# Override Python to use raw matching
contains-snippet --snippet-file notice.txt \
  --infer-comment-prefix \
  --comment-prefix-map ".py=raw" \
  src/*.py
```

#### Precedence

1. `--comment-prefix` (highest) - forces global commented matching
2. `--infer-comment-prefix` + `--comment-prefix-map` - per-file inference
3. Default behavior - current hardcoded rules

## CI Checks

The following checks run on every push and pull request:

- **yamllint** - YAML linting for workflow files
- **pylint** - Python linting for source and test code
- **mypy** - Static type checking for source code
- **jscpd** - Duplicate code detection
- **pytest** - Unit, integration, and E2E tests
