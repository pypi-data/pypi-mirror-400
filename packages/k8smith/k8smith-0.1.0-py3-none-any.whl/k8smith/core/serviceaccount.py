"""ServiceAccount resource builder."""

from __future__ import annotations

from k8smith.core.models import ServiceAccountSpec


def build_serviceaccount(spec: ServiceAccountSpec) -> dict:
    """Build a Kubernetes ServiceAccount resource.

    Args:
        spec: ServiceAccount specification

    Returns:
        Kubernetes ServiceAccount resource as a dict
    """
    sa: dict = {
        "apiVersion": "v1",
        "kind": "ServiceAccount",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        sa["metadata"]["labels"] = spec.labels
    if spec.annotations:
        sa["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.automount_service_account_token is not None:
        sa["automountServiceAccountToken"] = spec.automount_service_account_token
    if spec.image_pull_secrets:
        sa["imagePullSecrets"] = spec.image_pull_secrets

    return sa
