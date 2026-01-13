"""Service resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import ServiceSpec


def build_service(spec: ServiceSpec) -> dict:
    """Build a Kubernetes Service resource.

    Args:
        spec: Service specification

    Returns:
        Kubernetes Service resource as a dict
    """
    return ResourceBuilder.build(spec, "v1", "Service")
