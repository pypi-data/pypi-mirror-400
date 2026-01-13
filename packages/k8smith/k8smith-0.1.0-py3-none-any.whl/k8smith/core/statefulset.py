"""StatefulSet resource builder."""

from __future__ import annotations

from k8smith.core.models import StatefulSetSpec


def build_statefulset(spec: StatefulSetSpec) -> dict:
    """Build a Kubernetes StatefulSet resource.

    Args:
        spec: StatefulSet specification

    Returns:
        Kubernetes StatefulSet resource as a dict
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

    statefulset: dict = {
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "serviceName": spec.service_name,
            "selector": {"matchLabels": selector},
            "template": template_dict,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        statefulset["metadata"]["labels"] = spec.labels
    if spec.annotations:
        statefulset["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.replicas is not None:
        statefulset["spec"]["replicas"] = spec.replicas
    if spec.volume_claim_templates:
        statefulset["spec"]["volumeClaimTemplates"] = spec.volume_claim_templates
    if spec.pod_management_policy:
        statefulset["spec"]["podManagementPolicy"] = spec.pod_management_policy
    if spec.update_strategy:
        statefulset["spec"]["updateStrategy"] = spec.update_strategy
    if spec.revision_history_limit is not None:
        statefulset["spec"]["revisionHistoryLimit"] = spec.revision_history_limit
    if spec.min_ready_seconds is not None:
        statefulset["spec"]["minReadySeconds"] = spec.min_ready_seconds
    if spec.persistent_volume_claim_retention_policy:
        statefulset["spec"]["persistentVolumeClaimRetentionPolicy"] = (
            spec.persistent_volume_claim_retention_policy
        )

    return statefulset
