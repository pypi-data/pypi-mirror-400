"""Secret resource builder."""

from __future__ import annotations

from k8smith.core.models import SecretSpec


def build_secret(spec: SecretSpec) -> dict:
    """Build a Kubernetes Secret resource.

    Args:
        spec: Secret specification

    Returns:
        Kubernetes Secret resource as a dict
    """
    secret: dict = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
    }

    if spec.type:
        secret["type"] = spec.type

    # Add optional metadata fields
    if spec.labels:
        secret["metadata"]["labels"] = spec.labels
    if spec.annotations:
        secret["metadata"]["annotations"] = spec.annotations

    # Add data fields
    if spec.data:
        secret["data"] = spec.data
    if spec.string_data:
        secret["stringData"] = spec.string_data
    if spec.immutable is not None:
        secret["immutable"] = spec.immutable

    return secret
