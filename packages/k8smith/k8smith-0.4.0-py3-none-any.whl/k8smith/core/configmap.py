"""ConfigMap resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import ConfigMapSpec


def build_configmap(spec: ConfigMapSpec) -> dict:
    """Build a Kubernetes ConfigMap resource.

    Args:
        spec: ConfigMap specification

    Returns:
        Kubernetes ConfigMap resource as a dict
    """
    return ResourceBuilder.build(
        spec,
        "v1",
        "ConfigMap",
        include_spec=False,
        top_level_fields={"data", "binary_data", "immutable"},
    )
