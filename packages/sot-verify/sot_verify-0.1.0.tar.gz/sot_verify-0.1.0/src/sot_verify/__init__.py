"""
sot-verify

Quick verification for Source of Truth (.sot) files
Lightweight wrapper around sot-validator for CI/CD pipelines

For detailed validation with warnings, use sot-validator instead.

https://github.com/frmoretto/clarity-gate
"""

# Re-export everything from sot-validator
from sot_validator import (
    validate,
    is_valid,
    detect,
    validate_file,
    ValidationError,
    ValidationResult,
    __version__,
)

__all__ = [
    'validate',
    'is_valid',
    'detect',
    'validate_file',
    'ValidationError',
    'ValidationResult',
    '__version__',
]
