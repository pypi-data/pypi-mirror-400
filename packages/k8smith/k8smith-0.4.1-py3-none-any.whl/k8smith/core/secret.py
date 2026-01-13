"""Secret resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import SecretSpec


def build_secret(spec: SecretSpec) -> dict:
    """Build a Kubernetes Secret resource.

    Args:
        spec: Secret specification

    Returns:
        Kubernetes Secret resource as a dict
    """
    return ResourceBuilder.build(
        spec,
        "v1",
        "Secret",
        include_spec=False,
        top_level_fields={"type", "data", "string_data", "immutable"},
    )
