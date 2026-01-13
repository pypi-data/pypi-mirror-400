"""Namespace resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import NamespaceSpec


def build_namespace(spec: NamespaceSpec) -> dict:
    """Build a Kubernetes Namespace resource.

    Args:
        spec: Namespace specification

    Returns:
        Kubernetes Namespace resource as a dict
    """
    return ResourceBuilder.build(spec, "v1", "Namespace", include_spec=False)
