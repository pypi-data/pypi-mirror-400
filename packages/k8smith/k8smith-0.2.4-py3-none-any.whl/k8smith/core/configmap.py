"""ConfigMap resource builder."""

from __future__ import annotations

from k8smith.core.models import ConfigMapSpec


def build_configmap(spec: ConfigMapSpec) -> dict:
    """Build a Kubernetes ConfigMap resource.

    Args:
        spec: ConfigMap specification

    Returns:
        Kubernetes ConfigMap resource as a dict
    """
    configmap: dict = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        configmap["metadata"]["labels"] = spec.labels
    if spec.annotations:
        configmap["metadata"]["annotations"] = spec.annotations

    # Add data fields
    if spec.data:
        configmap["data"] = spec.data
    if spec.binary_data:
        configmap["binaryData"] = spec.binary_data
    if spec.immutable is not None:
        configmap["immutable"] = spec.immutable

    return configmap
