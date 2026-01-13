"""Generic resource builder for Kubernetes manifests.

Provides a reusable builder that handles common patterns across all resource types:
- Routing fields to metadata vs spec sections
- Auto-transforming KubeModel instances to dicts
- Supporting resources with different structures (top-level fields, no spec, etc.)
"""

from __future__ import annotations

from typing import Any

from k8smith.core.models import KubeModel


class ResourceBuilder:
    """Generic builder for Kubernetes resources.

    Handles the common pattern of building K8s resources by:
    1. Creating the base structure (apiVersion, kind, metadata, spec)
    2. Routing fields to the appropriate location based on field name
    3. Auto-transforming nested KubeModel instances to dicts

    Examples:
        Simple resource (all fields go to spec):
        >>> ResourceBuilder.build(spec, "v1", "Service")

        Metadata-only resource (no spec section):
        >>> ResourceBuilder.build(spec, "v1", "Namespace", include_spec=False)

        Resource with top-level fields (RBAC):
        >>> ResourceBuilder.build(spec, "rbac.authorization.k8s.io/v1", "Role",
        ...                       top_level_fields={"rules"})

        Resource with custom field handling:
        >>> ResourceBuilder.build(spec, "apps/v1", "Deployment",
        ...                       skip_fields={"selector", "template"})
    """

    METADATA_FIELDS = {"name", "namespace", "labels", "annotations"}

    @classmethod
    def build(
        cls,
        spec: KubeModel,
        api_version: str,
        kind: str,
        *,
        include_spec: bool = True,
        top_level_fields: set[str] | None = None,
        skip_fields: set[str] | None = None,
    ) -> dict[str, Any]:
        """Build a Kubernetes resource from a spec model.

        Args:
            spec: The specification model (e.g., ServiceSpec, IngressSpec)
            api_version: Kubernetes API version (e.g., "v1", "apps/v1")
            kind: Resource kind (e.g., "Service", "Deployment")
            include_spec: Whether to include a spec section (False for Namespace)
            top_level_fields: Field names that go at resource root, not in spec
                             (e.g., {"rules"} for Role, {"roleRef", "subjects"} for RoleBinding)
            skip_fields: Field names to skip (handled manually by the caller)

        Returns:
            Kubernetes resource as a dict ready for YAML serialization
        """
        resource: dict[str, Any] = {
            "apiVersion": api_version,
            "kind": kind,
            "metadata": {},
        }
        if include_spec:
            resource["spec"] = {}

        top_level_fields = top_level_fields or set()
        skip_fields = skip_fields or set()

        for field_name, field_info in type(spec).model_fields.items():
            if field_name in skip_fields:
                continue

            val = getattr(spec, field_name)
            if val is None:
                continue

            # Get the Kubernetes field name (alias or original)
            key = field_info.alias or field_name

            # Auto-transform nested models to dicts
            val = cls._transform_value(val)

            # Route to the appropriate location
            if field_name in cls.METADATA_FIELDS:
                if val:  # Skip empty labels/annotations
                    resource["metadata"][key] = val
            elif field_name in top_level_fields:
                resource[key] = val
            elif include_spec:
                resource["spec"][key] = val

        return resource

    @classmethod
    def _transform_value(cls, val: Any) -> Any:
        """Transform KubeModel instances to dicts recursively.

        Handles both single KubeModel instances and lists of them.
        """
        if isinstance(val, KubeModel):
            return val.to_dict()
        elif isinstance(val, list) and val and isinstance(val[0], KubeModel):
            return [v.to_dict() for v in val]
        return val
