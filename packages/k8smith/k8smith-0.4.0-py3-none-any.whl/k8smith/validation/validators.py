"""Manifest validators."""

from __future__ import annotations

import warnings
from typing import Any

from k8smith.validation.core import (
    ValidationError,
    ValidationMode,
    ValidationResult,
)


def validate_manifest(
    manifest: dict[str, Any],
    *,
    structural: ValidationMode = ValidationMode.STRICT,
    cross_reference: ValidationMode = ValidationMode.NONE,
    best_practice: ValidationMode = ValidationMode.NONE,
) -> ValidationResult:
    """Validate a Kubernetes manifest.

    Args:
        manifest: The Kubernetes resource dict to validate
        structural: Mode for structural validation (required fields, valid combinations)
        cross_reference: Mode for cross-reference validation (volumes, ports, selectors)
        best_practice: Mode for best practices validation (resources, probes)

    Returns:
        ValidationResult containing all issues found

    Raises:
        ValidationError: In strict mode, if any issues are found in that category

    Example:
        >>> manifest = build_deployment(spec)
        >>> result = validate_manifest(
        ...     manifest,
        ...     structural=ValidationMode.STRICT,
        ...     cross_reference=ValidationMode.CHECK,
        ...     best_practice=ValidationMode.NONE,
        ... )
    """
    result = ValidationResult()

    # Run validators based on mode
    if structural != ValidationMode.NONE:
        _validate_structural(manifest, result)
        _handle_mode(result, structural, "structural")

    if cross_reference != ValidationMode.NONE:
        _validate_cross_reference(manifest, result)
        _handle_mode(result, cross_reference, "cross_reference")

    if best_practice != ValidationMode.NONE:
        _validate_best_practice(manifest, result)
        _handle_mode(result, best_practice, "best_practice")

    return result


def _handle_mode(result: ValidationResult, mode: ValidationMode, category: str) -> None:
    """Handle validation results based on mode."""
    category_issues = [i for i in result.issues if i.category == category]

    if not category_issues:
        return

    if mode == ValidationMode.CHECK:
        for issue in category_issues:
            warnings.warn(str(issue), UserWarning, stacklevel=4)
    elif mode == ValidationMode.STRICT:
        errors = [i for i in category_issues if i.severity.value == "error"]
        if errors:
            raise ValidationError(errors)


# =============================================================================
# Structural Validators
# =============================================================================


def _validate_structural(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate structural requirements."""
    kind = manifest.get("kind", "")

    # Common metadata validation
    _validate_metadata(manifest, result)

    # Kind-specific validation
    validators = {
        "Deployment": _validate_deployment_structure,
        "StatefulSet": _validate_statefulset_structure,
        "DaemonSet": _validate_daemonset_structure,
        "CronJob": _validate_cronjob_structure,
        "Service": _validate_service_structure,
    }

    if kind in validators:
        validators[kind](manifest, result)


def _validate_metadata(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate common metadata fields."""
    if "apiVersion" not in manifest:
        result.error("apiVersion", "Missing required field", "structural")

    if "kind" not in manifest:
        result.error("kind", "Missing required field", "structural")

    metadata = manifest.get("metadata", {})
    if not metadata:
        result.error("metadata", "Missing required field", "structural")
        return

    if "name" not in metadata:
        result.error("metadata.name", "Missing required field", "structural")

    # Namespace is required for namespaced resources (not Namespace itself)
    kind = manifest.get("kind", "")
    cluster_scoped = ("Namespace", "ClusterRole", "ClusterRoleBinding")
    if kind not in cluster_scoped and "namespace" not in metadata:
        result.error("metadata.namespace", "Missing required field", "structural")


def _validate_deployment_structure(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate Deployment-specific structure."""
    spec = manifest.get("spec", {})
    if not spec:
        result.error("spec", "Missing required field", "structural")
        return

    if "selector" not in spec:
        result.error("spec.selector", "Missing required field", "structural")

    if "template" not in spec:
        result.error("spec.template", "Missing required field", "structural")
        return

    _validate_pod_template(spec.get("template", {}), "spec.template", result)


def _validate_statefulset_structure(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate StatefulSet-specific structure."""
    spec = manifest.get("spec", {})
    if not spec:
        result.error("spec", "Missing required field", "structural")
        return

    if "selector" not in spec:
        result.error("spec.selector", "Missing required field", "structural")

    if "serviceName" not in spec:
        result.error("spec.serviceName", "Missing required field", "structural")

    if "template" not in spec:
        result.error("spec.template", "Missing required field", "structural")
        return

    _validate_pod_template(spec.get("template", {}), "spec.template", result)


def _validate_daemonset_structure(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate DaemonSet-specific structure."""
    spec = manifest.get("spec", {})
    if not spec:
        result.error("spec", "Missing required field", "structural")
        return

    if "selector" not in spec:
        result.error("spec.selector", "Missing required field", "structural")

    if "template" not in spec:
        result.error("spec.template", "Missing required field", "structural")
        return

    _validate_pod_template(spec.get("template", {}), "spec.template", result)


def _validate_cronjob_structure(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate CronJob-specific structure."""
    spec = manifest.get("spec", {})
    if not spec:
        result.error("spec", "Missing required field", "structural")
        return

    if "schedule" not in spec:
        result.error("spec.schedule", "Missing required field", "structural")

    if "jobTemplate" not in spec:
        result.error("spec.jobTemplate", "Missing required field", "structural")


def _validate_service_structure(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate Service-specific structure."""
    spec = manifest.get("spec", {})
    if not spec:
        result.error("spec", "Missing required field", "structural")
        return

    # Services need either selector or externalName
    svc_type = spec.get("type", "ClusterIP")
    if svc_type == "ExternalName":
        if "externalName" not in spec:
            result.error(
                "spec.externalName",
                "ExternalName service requires externalName field",
                "structural",
            )
    elif "selector" not in spec:
        result.warning(
            "spec.selector",
            "Service without selector won't route to any pods",
            "structural",
        )


def _validate_pod_template(template: dict[str, Any], path: str, result: ValidationResult) -> None:
    """Validate pod template structure."""
    if "spec" not in template:
        result.error(f"{path}.spec", "Missing required field", "structural")
        return

    spec = template["spec"]
    containers = spec.get("containers", [])
    if not containers:
        result.error(f"{path}.spec.containers", "At least one container is required", "structural")
        return

    for i, container in enumerate(containers):
        _validate_container(container, f"{path}.spec.containers[{i}]", result)


def _validate_container(container: dict[str, Any], path: str, result: ValidationResult) -> None:
    """Validate container structure."""
    if "name" not in container:
        result.error(f"{path}.name", "Missing required field", "structural")

    if "image" not in container:
        result.error(f"{path}.image", "Missing required field", "structural")


# =============================================================================
# Cross-Reference Validators
# =============================================================================


def _validate_cross_reference(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate cross-references within the manifest."""
    kind = manifest.get("kind", "")

    if kind in ("Deployment", "StatefulSet", "DaemonSet"):
        _validate_workload_cross_refs(manifest, result)


def _validate_workload_cross_refs(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate cross-references in workload resources."""
    spec = manifest.get("spec", {})
    template = spec.get("template", {})
    pod_spec = template.get("spec", {})

    # Check volume mounts reference existing volumes
    _validate_volume_mounts(pod_spec, result)

    # Check selector matches pod labels
    _validate_selector_matches_labels(spec, template, result)

    # Check container port names are unique
    _validate_unique_port_names(pod_spec, result)


def _validate_volume_mounts(pod_spec: dict[str, Any], result: ValidationResult) -> None:
    """Validate that volume mounts reference existing volumes."""
    volumes = pod_spec.get("volumes", [])
    volume_names = {v.get("name") for v in volumes if v.get("name")}

    all_containers = pod_spec.get("containers", []) + pod_spec.get("initContainers", [])

    for i, container in enumerate(all_containers):
        container_name = container.get("name", f"container[{i}]")
        for mount in container.get("volumeMounts", []):
            mount_name = mount.get("name")
            if mount_name and mount_name not in volume_names:
                result.error(
                    f"spec.template.spec.containers.{container_name}.volumeMounts",
                    f"Volume mount '{mount_name}' references non-existent volume",
                    "cross_reference",
                )


def _validate_selector_matches_labels(
    spec: dict[str, Any], template: dict[str, Any], result: ValidationResult
) -> None:
    """Validate that selector matchLabels are present in pod labels."""
    selector = spec.get("selector", {})
    match_labels = selector.get("matchLabels", {})
    pod_labels = template.get("metadata", {}).get("labels", {})

    for key, value in match_labels.items():
        if key not in pod_labels:
            result.error(
                "spec.selector.matchLabels",
                f"Selector label '{key}' not found in pod template labels",
                "cross_reference",
            )
        elif pod_labels[key] != value:
            result.error(
                "spec.selector.matchLabels",
                f"Selector label '{key}={value}' doesn't match pod label '{key}={pod_labels[key]}'",
                "cross_reference",
            )


def _validate_unique_port_names(pod_spec: dict[str, Any], result: ValidationResult) -> None:
    """Validate that container port names are unique within a pod."""
    all_containers = pod_spec.get("containers", []) + pod_spec.get("initContainers", [])
    port_names: dict[str, str] = {}  # port_name -> container_name

    for container in all_containers:
        container_name = container.get("name", "unknown")
        for port in container.get("ports", []):
            port_name = port.get("name")
            if port_name:
                if port_name in port_names:
                    other = port_names[port_name]
                    result.error(
                        f"spec.template.spec.containers.{container_name}.ports",
                        f"Port name '{port_name}' already used by container '{other}'",
                        "cross_reference",
                    )
                else:
                    port_names[port_name] = container_name


# =============================================================================
# Best Practice Validators
# =============================================================================


def _validate_best_practice(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate best practices."""
    kind = manifest.get("kind", "")

    if kind in ("Deployment", "StatefulSet", "DaemonSet"):
        _validate_workload_best_practices(manifest, result)


def _validate_workload_best_practices(manifest: dict[str, Any], result: ValidationResult) -> None:
    """Validate best practices for workload resources."""
    spec = manifest.get("spec", {})
    template = spec.get("template", {})
    pod_spec = template.get("spec", {})

    containers = pod_spec.get("containers", [])
    for i, container in enumerate(containers):
        container_name = container.get("name", f"container[{i}]")
        path = f"spec.template.spec.containers.{container_name}"

        # Check for resource requests/limits
        resources = container.get("resources", {})
        if not resources:
            result.warning(path, "Container has no resource requests or limits", "best_practice")
        else:
            if not resources.get("requests"):
                result.warning(f"{path}.resources", "No resource requests defined", "best_practice")
            if not resources.get("limits"):
                result.warning(f"{path}.resources", "No resource limits defined", "best_practice")

        # Check for probes
        if not container.get("readinessProbe"):
            result.warning(f"{path}", "No readiness probe defined", "best_practice")
        if not container.get("livenessProbe"):
            result.warning(f"{path}", "No liveness probe defined", "best_practice")

        # Check for latest tag
        image = container.get("image", "")
        if image.endswith(":latest") or ":" not in image:
            result.warning(
                f"{path}.image",
                "Using 'latest' tag or no tag - consider using specific version",
                "best_practice",
            )

    # Check for pod security context
    if not pod_spec.get("securityContext"):
        result.warning(
            "spec.template.spec.securityContext",
            "No pod security context defined",
            "best_practice",
        )
