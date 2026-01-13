"""GCPBackendPolicy resource builder for GKE."""

from k8smith.gke.models import GCPBackendPolicySpec


def build_gcp_backend_policy(spec: GCPBackendPolicySpec) -> dict:
    """Build a GKE GCPBackendPolicy resource.

    Args:
        spec: GCPBackendPolicy specification

    Returns:
        GCPBackendPolicy resource as a dict
    """
    policy: dict = {
        "apiVersion": "networking.gke.io/v1",
        "kind": "GCPBackendPolicy",
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
        policy["metadata"]["labels"] = spec.labels
    if spec.annotations:
        policy["metadata"]["annotations"] = spec.annotations

    return policy
