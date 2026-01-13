# Validation

Optional manifest validation utilities.

## Usage

```python
from k8smith.validation import validate_manifest, ValidationMode

result = validate_manifest(
    manifest,
    structural=ValidationMode.STRICT,
    cross_reference=ValidationMode.CHECK,
    best_practice=ValidationMode.NONE,
)

if result.errors:
    print("Errors:", result.errors)
if result.warnings:
    print("Warnings:", result.warnings)
```

## Validation Modes

::: k8smith.validation.core.ValidationMode

## Functions

::: k8smith.validation.validators.validate_manifest

## Result Types

::: k8smith.validation.core.ValidationResult

::: k8smith.validation.core.ValidationIssue
