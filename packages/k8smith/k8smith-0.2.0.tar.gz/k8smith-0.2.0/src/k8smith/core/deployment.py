"""Deployment resource builder."""

from __future__ import annotations

from k8smith.core.models import DeploymentSpec


def build_deployment(spec: DeploymentSpec) -> dict:
    """Build a Kubernetes Deployment resource.

    Args:
        spec: Deployment specification

    Returns:
        Kubernetes Deployment resource as a dict

    Example:
        >>> from k8smith.core.models import (
        ...     Container, DeploymentSpec, PodSpec, PodTemplateSpec,
        ... )
        >>> spec = DeploymentSpec(
        ...     name="web",
        ...     namespace="production",
        ...     replicas=3,
        ...     template=PodTemplateSpec(
        ...         spec=PodSpec(
        ...             containers=[Container(name="web", image="nginx:1.25")]
        ...         )
        ...     ),
        ... )
        >>> deployment = build_deployment(spec)
    """
    # Default selector if not specified
    selector = spec.selector or {"app.kubernetes.io/name": spec.name}

    # Build pod template with selector merged into labels
    template_dict = spec.template.to_dict()
    template_dict.setdefault("metadata", {})
    template_dict["metadata"]["labels"] = {
        **selector,
        **template_dict["metadata"].get("labels", {}),
    }

    deployment: dict = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "selector": {"matchLabels": selector},
            "template": template_dict,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        deployment["metadata"]["labels"] = spec.labels
    if spec.annotations:
        deployment["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.replicas is not None:
        deployment["spec"]["replicas"] = spec.replicas
    if spec.strategy:
        deployment["spec"]["strategy"] = spec.strategy
    if spec.min_ready_seconds is not None:
        deployment["spec"]["minReadySeconds"] = spec.min_ready_seconds
    if spec.revision_history_limit is not None:
        deployment["spec"]["revisionHistoryLimit"] = spec.revision_history_limit
    if spec.progress_deadline_seconds is not None:
        deployment["spec"]["progressDeadlineSeconds"] = spec.progress_deadline_seconds
    if spec.paused is not None:
        deployment["spec"]["paused"] = spec.paused

    return deployment
