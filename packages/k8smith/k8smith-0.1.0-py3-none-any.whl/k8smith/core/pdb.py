"""PodDisruptionBudget resource builder."""

from __future__ import annotations

from k8smith.core.models import PDBSpec


def build_pdb(spec: PDBSpec) -> dict:
    """Build a Kubernetes PodDisruptionBudget resource.

    Args:
        spec: PDB specification

    Returns:
        Kubernetes PodDisruptionBudget resource as a dict
    """
    pdb: dict = {
        "apiVersion": "policy/v1",
        "kind": "PodDisruptionBudget",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "selector": {
                "matchLabels": spec.selector,
            },
        },
    }

    # Add optional metadata fields
    if spec.labels:
        pdb["metadata"]["labels"] = spec.labels
    if spec.annotations:
        pdb["metadata"]["annotations"] = spec.annotations

    # Add disruption budget (one of minAvailable or maxUnavailable)
    if spec.min_available is not None:
        pdb["spec"]["minAvailable"] = spec.min_available
    if spec.max_unavailable is not None:
        pdb["spec"]["maxUnavailable"] = spec.max_unavailable

    return pdb
