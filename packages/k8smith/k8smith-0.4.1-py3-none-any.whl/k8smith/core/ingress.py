"""Ingress resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import IngressSpec


def build_ingress(spec: IngressSpec) -> dict:
    """Build a Kubernetes Ingress resource.

    Args:
        spec: Ingress specification

    Returns:
        Kubernetes Ingress resource as a dict
    """
    return ResourceBuilder.build(spec, "networking.k8s.io/v1", "Ingress")
