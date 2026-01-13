# CDD Utils

General utilities for AI-assisted development.

Part of the [Contract-Driven Development](https://github.com/thegdyne/cdd) ecosystem.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   cdd-flow         Orchestration layer                         │
│                    ctx, land, undo, checkpoint                  │
│      │                                                          │
│      ├───────────► cdd-context     Context generation           │
│      │                             PROJECT_CONTEXT.md           │
│      │                                                          │
│      └───────────► cdd-tooling     Verification                 │
│                    analyze, lint, test, compare                 │
│                                                                 │
│   cdd-utils        General utilities        ◄── YOU ARE HERE    │
│                    utf8 (encoding hygiene)                      │
│                                                                 │
│   cdd              Methodology (spec only)                      │
│                    SPEC.md, README.md                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
pip install cdd-utils

# Or with pipx (recommended for CLI use)
pipx install cdd-utils

# From source (editable)
git clone https://github.com/thegdyne/cdd-utils.git
cd cdd-utils
pip install -e ".[dev]"
```

## Commands

| Command | Description |
|---------|-------------|
| `cdd-utils utf8` | UTF-8 corruption detection and ASCII normalization |

## utf8 - Encoding Hygiene

AI-generated code often contains encoding issues: smart quotes, corrupted UTF-8 sequences, invisible characters. The `utf8` command detects and fixes these.

### Modes

| Mode | Flag | Description |
|------|------|-------------|
| Report | `--report` | Scan and list all non-ASCII characters |
| Preview | `--dry-run` | Show what would be fixed |
| Smart Preview | `--dry-run --smart` | Categorize as legitimate vs suspicious |
| Fix All | `--fix` | Normalize ALL non-ASCII to ASCII |
| Smart Fix | `--smart-fix` | Fix only suspicious (clustered) characters |

### Smart Mode

Smart mode distinguishes between:

- **Legitimate**: Isolated non-ASCII surrounded by ASCII (intentional symbols like `•`, `↻`, `→`)
- **Suspicious**: Clustered non-ASCII adjacent to each other (likely corruption like `â†'`)

### Examples

```bash
# Scan a directory for non-ASCII
cdd-utils utf8 --report src/

# Preview fixes for a file
cdd-utils utf8 --dry-run src/main.py

# See legitimate vs suspicious breakdown
cdd-utils utf8 --dry-run --smart src/main.py

# Fix only corrupted sequences, keep intentional Unicode
cdd-utils utf8 --smart-fix src/main.py

# Fix everything (normalize all to ASCII)
cdd-utils utf8 --fix src/main.py

# Filter by extension
cdd-utils utf8 --report src/ --ext .py .scd
```

### What It Detects

- Invalid/corrupted UTF-8 byte sequences
- Smart quotes and curly apostrophes (`"` `"` `'` `'`)
- Em/en dashes and fancy hyphens (`—` `–`)
- Non-breaking spaces and zero-width characters
- Unicode arrows, bullets, symbols
- Replacement characters (corruption indicator)

### Backups

Both `--fix` and `--smart-fix` create timestamped backups before modifying files:

```
_utf8_backups_20250101_120000/
├── src/
│   └── main.py
```

## Suggested Alias

```bash
alias cu='cdd-utils'
# Usage: cu utf8 --report src/
```

## Development

```bash
git clone https://github.com/thegdyne/cdd-utils.git
cd cdd-utils
pip install -e ".[dev]"
pytest
```

## License

MIT
