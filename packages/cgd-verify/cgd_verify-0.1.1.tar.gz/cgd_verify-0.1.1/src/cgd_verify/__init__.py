"""
cgd-verify

Quick verification for Clarity-Gated Document (.cgd) files
Lightweight wrapper around cgd-validator for CI/CD pipelines

For detailed validation with warnings, use cgd-validator instead.

https://github.com/frmoretto/clarity-gate
"""

# Re-export everything from cgd-validator
from cgd_validator import (
    validate,
    is_valid,
    detect,
    validate_file,
    parse_frontmatter,
    ValidationError,
    ValidationResult,
    __version__,
)

__all__ = [
    'validate',
    'is_valid',
    'detect',
    'validate_file',
    'parse_frontmatter',
    'ValidationError',
    'ValidationResult',
    '__version__',
]
