"""PodMonitoring and ClusterPodMonitoring resource builders for GKE."""

from k8smith.gke.models import ClusterPodMonitoringSpec, PodMonitoringSpec


def build_pod_monitoring(spec: PodMonitoringSpec) -> dict:
    """Build a GKE PodMonitoring resource.

    Args:
        spec: PodMonitoring specification

    Returns:
        PodMonitoring resource as a dict
    """
    monitoring: dict = {
        "apiVersion": "monitoring.googleapis.com/v1",
        "kind": "PodMonitoring",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "selector": spec.selector,
            "endpoints": spec.endpoints,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        monitoring["metadata"]["labels"] = spec.labels
    if spec.annotations:
        monitoring["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.target_labels:
        monitoring["spec"]["targetLabels"] = spec.target_labels

    return monitoring


def build_cluster_pod_monitoring(spec: ClusterPodMonitoringSpec) -> dict:
    """Build a GKE ClusterPodMonitoring resource.

    Args:
        spec: ClusterPodMonitoring specification

    Returns:
        ClusterPodMonitoring resource as a dict
    """
    monitoring: dict = {
        "apiVersion": "monitoring.googleapis.com/v1",
        "kind": "ClusterPodMonitoring",
        "metadata": {
            "name": spec.name,
        },
        "spec": {
            "selector": spec.selector,
            "endpoints": spec.endpoints,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        monitoring["metadata"]["labels"] = spec.labels
    if spec.annotations:
        monitoring["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.target_labels:
        monitoring["spec"]["targetLabels"] = spec.target_labels

    return monitoring
