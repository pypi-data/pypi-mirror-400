# cgd-verify

Quick pass/fail verification for Clarity-Gated Document (`.cgd`) files — optimized for CI/CD pipelines.

[![PyPI version](https://badge.fury.io/py/cgd-verify.svg)](https://pypi.org/project/cgd-verify/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## When to Use

| Tool | Use Case |
|------|----------|
| **cgd-verify** | CI/CD pipelines, git hooks, quick checks |
| **cgd-validator** | Detailed reports, debugging, development |

## Installation

```bash
pip install cgd-verify
```

## CLI Usage

```bash
# Quick check - exit 0 if valid, exit 1 if invalid
cgd-verify document.cgd

# Multiple files
cgd-verify docs/*.cgd

# Silent mode (only exit code, no output)
cgd-verify document.cgd --silent
```

## In CI/CD

```yaml
# GitHub Actions
- run: pip install cgd-verify && cgd-verify docs/*.cgd

# Pre-commit hook
cgd-verify $(git diff --cached --name-only -- '*.cgd')
```

## Python API

```python
# Re-exports everything from cgd-validator
from cgd_verify import validate, is_valid, detect

if is_valid(content):
    print('Valid')
```

## Related

- [cgd-validator](https://pypi.org/project/cgd-validator/) - Detailed validation with warnings
- [sot-verify](https://pypi.org/project/sot-verify/) - Quick verification for .sot files
- [Clarity Gate](https://github.com/frmoretto/clarity-gate) - Full ecosystem

## License

CC BY 4.0
