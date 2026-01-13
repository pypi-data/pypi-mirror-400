"""DaemonSet resource builder."""

from __future__ import annotations

from k8smith.core.models import DaemonSetSpec


def build_daemonset(spec: DaemonSetSpec) -> dict:
    """Build a Kubernetes DaemonSet resource.

    Args:
        spec: DaemonSet specification

    Returns:
        Kubernetes DaemonSet resource as a dict
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

    daemonset: dict = {
        "apiVersion": "apps/v1",
        "kind": "DaemonSet",
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
        daemonset["metadata"]["labels"] = spec.labels
    if spec.annotations:
        daemonset["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.update_strategy:
        daemonset["spec"]["updateStrategy"] = spec.update_strategy
    if spec.min_ready_seconds is not None:
        daemonset["spec"]["minReadySeconds"] = spec.min_ready_seconds
    if spec.revision_history_limit is not None:
        daemonset["spec"]["revisionHistoryLimit"] = spec.revision_history_limit

    return daemonset
