"""Deployment resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import DeploymentSpec


def build_deployment(spec: DeploymentSpec) -> dict:
    """Build a Kubernetes Deployment resource.

    Note: selector and template are handled manually because:
    1. selector must be wrapped as {"matchLabels": ...} in output
    2. selector labels must be merged into template.metadata.labels
       (Kubernetes requires pod labels to match the selector)
    3. selector auto-generates from spec.name if not provided
    These cross-field dependencies can't be expressed in ResourceBuilder.

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
    # Build selector and merge into template labels
    selector = spec.selector or {"app.kubernetes.io/name": spec.name}
    template_dict = spec.template.to_dict()
    template_dict.setdefault("metadata", {})
    template_dict["metadata"]["labels"] = {
        **selector,
        **template_dict["metadata"].get("labels", {}),
    }

    # Use ResourceBuilder for everything except selector and template
    resource = ResourceBuilder.build(
        spec, "apps/v1", "Deployment", skip_fields={"selector", "template"}
    )
    resource["spec"]["selector"] = {"matchLabels": selector}
    resource["spec"]["template"] = template_dict

    return resource
