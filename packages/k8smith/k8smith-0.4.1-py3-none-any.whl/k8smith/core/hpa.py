"""HorizontalPodAutoscaler resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import HPASpec


def build_hpa(spec: HPASpec) -> dict:
    """Build a Kubernetes HorizontalPodAutoscaler resource.

    Args:
        spec: HPA specification

    Returns:
        Kubernetes HorizontalPodAutoscaler resource as a dict
    """
    return ResourceBuilder.build(spec, "autoscaling/v2", "HorizontalPodAutoscaler")
