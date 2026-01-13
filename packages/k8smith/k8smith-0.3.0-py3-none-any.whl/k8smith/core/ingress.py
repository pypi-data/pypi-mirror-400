"""Ingress resource builder."""

from __future__ import annotations

from k8smith.core.models import IngressSpec


def build_ingress(spec: IngressSpec) -> dict:
    """Build a Kubernetes Ingress resource.

    Args:
        spec: Ingress specification

    Returns:
        Kubernetes Ingress resource as a dict
    """
    ingress: dict = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {},
    }

    # Add optional metadata fields
    if spec.labels:
        ingress["metadata"]["labels"] = spec.labels
    if spec.annotations:
        ingress["metadata"]["annotations"] = spec.annotations

    # Build spec
    if spec.ingress_class_name:
        ingress["spec"]["ingressClassName"] = spec.ingress_class_name
    if spec.default_backend:
        ingress["spec"]["defaultBackend"] = spec.default_backend.to_dict()
    if spec.rules:
        ingress["spec"]["rules"] = [r.to_dict() for r in spec.rules]
    if spec.tls:
        ingress["spec"]["tls"] = [t.to_dict() for t in spec.tls]

    return ingress
