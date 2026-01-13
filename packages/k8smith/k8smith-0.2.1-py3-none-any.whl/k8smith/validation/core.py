"""Core validation types and infrastructure."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class ValidationMode(Enum):
    """Validation mode controlling how issues are reported.

    Attributes:
        NONE: Silent - no warnings or errors raised
        CHECK: Emit warnings for issues but don't raise exceptions
        STRICT: Raise exception containing all detected issues
    """

    NONE = "none"
    CHECK = "check"
    STRICT = "strict"


class ValidationSeverity(Enum):
    """Severity level for validation issues."""

    ERROR = "error"  # Structural issues - will cause K8s to reject
    WARNING = "warning"  # Best practices - may cause runtime issues


@dataclass
class ValidationIssue:
    """A single validation issue found in a manifest.

    Attributes:
        path: JSON path to the problematic field (e.g., "spec.template.spec.containers[0]")
        message: Human-readable description of the issue
        severity: Whether this is an error or warning
        category: Type of validation that caught this (structural, cross_reference, best_practice)
    """

    path: str
    message: str
    severity: ValidationSeverity
    category: Literal["structural", "cross_reference", "best_practice"]

    def __str__(self) -> str:
        prefix = "ERROR" if self.severity == ValidationSeverity.ERROR else "WARNING"
        return f"[{prefix}] {self.path}: {self.message}"


class ValidationError(Exception):
    """Raised in strict mode when validation issues are found."""

    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        lines = ["Validation failed with the following issues:"]
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


@dataclass
class ValidationResult:
    """Collection of validation issues from a validation run.

    Supports iteration and boolean checks:
        if result:  # True if there are issues
            for issue in result:
                print(issue)
    """

    issues: list[ValidationIssue] = field(default_factory=list)

    def add(
        self,
        path: str,
        message: str,
        severity: ValidationSeverity,
        category: Literal["structural", "cross_reference", "best_practice"],
    ) -> None:
        """Add a validation issue."""
        self.issues.append(ValidationIssue(path, message, severity, category))

    def error(
        self,
        path: str,
        message: str,
        category: Literal["structural", "cross_reference", "best_practice"],
    ) -> None:
        """Add an error-level issue."""
        self.add(path, message, ValidationSeverity.ERROR, category)

    def warning(
        self,
        path: str,
        message: str,
        category: Literal["structural", "cross_reference", "best_practice"],
    ) -> None:
        """Add a warning-level issue."""
        self.add(path, message, ValidationSeverity.WARNING, category)

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    def __bool__(self) -> bool:
        """True if there are any issues."""
        return len(self.issues) > 0

    def __iter__(self) -> Iterator[ValidationIssue]:
        return iter(self.issues)

    def __len__(self) -> int:
        return len(self.issues)

    def merge(self, other: ValidationResult) -> None:
        """Merge issues from another result into this one."""
        self.issues.extend(other.issues)
