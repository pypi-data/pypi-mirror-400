"""Service resource builder."""

from __future__ import annotations

from k8smith.core.models import ServiceSpec


def build_service(spec: ServiceSpec) -> dict:
    """Build a Kubernetes Service resource.

    Args:
        spec: Service specification

    Returns:
        Kubernetes Service resource as a dict
    """
    service: dict = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {},
    }

    # Add optional metadata fields
    if spec.labels:
        service["metadata"]["labels"] = spec.labels
    if spec.annotations:
        service["metadata"]["annotations"] = spec.annotations

    # Build spec - use to_dict() for ports
    if spec.selector:
        service["spec"]["selector"] = spec.selector
    if spec.ports:
        service["spec"]["ports"] = [p.to_dict() for p in spec.ports]
    if spec.type:
        service["spec"]["type"] = spec.type
    if spec.cluster_ip:
        service["spec"]["clusterIP"] = spec.cluster_ip
    if spec.external_name:
        service["spec"]["externalName"] = spec.external_name
    if spec.external_traffic_policy:
        service["spec"]["externalTrafficPolicy"] = spec.external_traffic_policy
    if spec.internal_traffic_policy:
        service["spec"]["internalTrafficPolicy"] = spec.internal_traffic_policy
    if spec.session_affinity:
        service["spec"]["sessionAffinity"] = spec.session_affinity
    if spec.load_balancer_ip:
        service["spec"]["loadBalancerIP"] = spec.load_balancer_ip
    if spec.load_balancer_source_ranges:
        service["spec"]["loadBalancerSourceRanges"] = spec.load_balancer_source_ranges

    return service
