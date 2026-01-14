# sot-verify

Quick pass/fail verification for Source of Truth (`.sot`) files — optimized for CI/CD pipelines.

[![PyPI version](https://badge.fury.io/py/sot-verify.svg)](https://pypi.org/project/sot-verify/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## When to Use

| Tool | Use Case |
|------|----------|
| **sot-verify** | CI/CD pipelines, git hooks, quick checks |
| **sot-validator** | Detailed reports, debugging, development |

## Installation

```bash
pip install sot-verify
```

## CLI Usage

```bash
# Quick check - exit 0 if valid, exit 1 if invalid
sot-verify project.sot

# Multiple files
sot-verify docs/*.sot

# Silent mode (only exit code, no output)
sot-verify project.sot --silent
```

## In CI/CD

```yaml
# GitHub Actions
- run: pip install sot-verify && sot-verify docs/*.sot

# Pre-commit hook
sot-verify $(git diff --cached --name-only -- '*.sot')
```

## Python API

```python
# Re-exports everything from sot-validator
from sot_verify import validate, is_valid, detect

if is_valid(content):
    print('Valid')
```

## Related

- [sot-validator](https://pypi.org/project/sot-validator/) - Detailed validation with warnings
- [cgd-verify](https://pypi.org/project/cgd-verify/) - Quick verification for .cgd files
- [Clarity Gate](https://github.com/frmoretto/clarity-gate) - Full ecosystem

## License

CC BY 4.0
