"""Kubernetes manifest validation.

Provides validators for structural, cross-reference, and best practice checks.

Example:
    >>> from k8smith.validation import validate_manifest, ValidationMode
    >>> manifest = build_deployment(spec)
    >>> result = validate_manifest(
    ...     manifest,
    ...     structural=ValidationMode.STRICT,
    ...     cross_reference=ValidationMode.CHECK,
    ...     best_practice=ValidationMode.NONE,
    ... )
"""

from __future__ import annotations

from k8smith.validation.core import (
    ValidationError,
    ValidationIssue,
    ValidationMode,
    ValidationResult,
    ValidationSeverity,
)
from k8smith.validation.validators import validate_manifest

__all__ = [
    "ValidationError",
    "ValidationIssue",
    "ValidationMode",
    "ValidationResult",
    "ValidationSeverity",
    "validate_manifest",
]
