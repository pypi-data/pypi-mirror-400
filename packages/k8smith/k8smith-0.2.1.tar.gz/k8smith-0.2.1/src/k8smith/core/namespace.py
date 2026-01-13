"""Namespace resource builder."""

from __future__ import annotations

from k8smith.core.models import NamespaceSpec


def build_namespace(spec: NamespaceSpec) -> dict:
    """Build a Kubernetes Namespace resource.

    Args:
        spec: Namespace specification

    Returns:
        Kubernetes Namespace resource as a dict
    """
    namespace: dict = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {
            "name": spec.name,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        namespace["metadata"]["labels"] = spec.labels
    if spec.annotations:
        namespace["metadata"]["annotations"] = spec.annotations

    return namespace
