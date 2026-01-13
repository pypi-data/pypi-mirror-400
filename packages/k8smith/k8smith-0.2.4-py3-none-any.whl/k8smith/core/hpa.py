"""HorizontalPodAutoscaler resource builder."""

from __future__ import annotations

from k8smith.core.models import HPASpec


def build_hpa(spec: HPASpec) -> dict:
    """Build a Kubernetes HorizontalPodAutoscaler resource.

    Args:
        spec: HPA specification

    Returns:
        Kubernetes HorizontalPodAutoscaler resource as a dict
    """
    hpa: dict = {
        "apiVersion": "autoscaling/v2",
        "kind": "HorizontalPodAutoscaler",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "scaleTargetRef": spec.scale_target_ref,
            "minReplicas": spec.min_replicas,
            "maxReplicas": spec.max_replicas,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        hpa["metadata"]["labels"] = spec.labels
    if spec.annotations:
        hpa["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.metrics:
        hpa["spec"]["metrics"] = spec.metrics
    if spec.behavior:
        hpa["spec"]["behavior"] = spec.behavior

    return hpa
