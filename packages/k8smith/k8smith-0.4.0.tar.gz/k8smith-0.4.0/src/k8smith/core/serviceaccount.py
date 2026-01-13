"""ServiceAccount resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import ServiceAccountSpec


def build_serviceaccount(spec: ServiceAccountSpec) -> dict:
    """Build a Kubernetes ServiceAccount resource.

    Args:
        spec: ServiceAccount specification

    Returns:
        Kubernetes ServiceAccount resource as a dict
    """
    return ResourceBuilder.build(
        spec,
        "v1",
        "ServiceAccount",
        include_spec=False,
        top_level_fields={"automount_service_account_token", "image_pull_secrets"},
    )
