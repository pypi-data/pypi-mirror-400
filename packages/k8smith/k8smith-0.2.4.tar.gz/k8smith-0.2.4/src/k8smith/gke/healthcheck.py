"""HealthCheckPolicy resource builder for GKE."""

from k8smith.gke.models import HealthCheckPolicySpec


def build_healthcheckpolicy(spec: HealthCheckPolicySpec) -> dict:
    """Build a GKE HealthCheckPolicy resource.

    Args:
        spec: HealthCheckPolicy specification

    Returns:
        HealthCheckPolicy resource as a dict
    """
    healthcheck: dict = {
        "apiVersion": "networking.gke.io/v1",
        "kind": "HealthCheckPolicy",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "targetRef": spec.target_ref,
            "default": spec.config,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        healthcheck["metadata"]["labels"] = spec.labels
    if spec.annotations:
        healthcheck["metadata"]["annotations"] = spec.annotations

    return healthcheck
