"""HTTPRoute resource builder for GKE."""

from k8smith.gke.models import HTTPRouteSpec


def build_httproute(spec: HTTPRouteSpec) -> dict:
    """Build a GKE HTTPRoute resource.

    Args:
        spec: HTTPRoute specification

    Returns:
        HTTPRoute resource as a dict
    """
    httproute: dict = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "parentRefs": spec.parent_refs,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        httproute["metadata"]["labels"] = spec.labels
    if spec.annotations:
        httproute["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.hostnames:
        httproute["spec"]["hostnames"] = spec.hostnames
    if spec.rules:
        httproute["spec"]["rules"] = spec.rules

    return httproute
