"""Gateway resource builder for GKE."""

from k8smith.gke.models import GatewaySpec


def build_gateway(spec: GatewaySpec) -> dict:
    """Build a GKE Gateway resource.

    Args:
        spec: Gateway specification

    Returns:
        Gateway resource as a dict
    """
    gateway: dict = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "gatewayClassName": spec.gateway_class_name,
            "listeners": spec.listeners,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        gateway["metadata"]["labels"] = spec.labels
    if spec.annotations:
        gateway["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.addresses:
        gateway["spec"]["addresses"] = spec.addresses

    return gateway
