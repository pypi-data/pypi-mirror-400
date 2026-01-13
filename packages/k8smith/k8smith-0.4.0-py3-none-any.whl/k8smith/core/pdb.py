"""PodDisruptionBudget resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import PDBSpec


def build_pdb(spec: PDBSpec) -> dict:
    """Build a Kubernetes PodDisruptionBudget resource.

    Note: selector is handled manually because it must be wrapped as
    {"matchLabels": selector} in the output.

    Args:
        spec: PDB specification

    Returns:
        Kubernetes PodDisruptionBudget resource as a dict
    """
    resource = ResourceBuilder.build(
        spec, "policy/v1", "PodDisruptionBudget", skip_fields={"selector"}
    )
    if spec.selector:
        resource["spec"]["selector"] = {"matchLabels": spec.selector}
    return resource
