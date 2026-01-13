"""DaemonSet resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import DaemonSetSpec


def build_daemonset(spec: DaemonSetSpec) -> dict:
    """Build a Kubernetes DaemonSet resource.

    Note: selector and template are handled manually because:
    1. selector must be wrapped as {"matchLabels": ...} in output
    2. selector labels must be merged into template.metadata.labels
       (Kubernetes requires pod labels to match the selector)
    3. selector auto-generates from spec.name if not provided
    These cross-field dependencies can't be expressed in ResourceBuilder.

    Args:
        spec: DaemonSet specification

    Returns:
        Kubernetes DaemonSet resource as a dict
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
        spec, "apps/v1", "DaemonSet", skip_fields={"selector", "template"}
    )
    resource["spec"]["selector"] = {"matchLabels": selector}
    resource["spec"]["template"] = template_dict

    return resource
