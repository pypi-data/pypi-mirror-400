"""RBAC resource builders.

Provides builders for Role, ClusterRole, RoleBinding, and ClusterRoleBinding resources.
"""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import (
    ClusterRoleBindingSpec,
    ClusterRoleSpec,
    RoleBindingSpec,
    RoleSpec,
)


def build_role(spec: RoleSpec) -> dict:
    """Build a Kubernetes Role resource.

    Args:
        spec: Role specification

    Returns:
        Kubernetes Role resource as a dict

    Example:
        >>> from k8smith.core.models import RoleSpec, PolicyRule
        >>> spec = RoleSpec(
        ...     name="pod-reader",
        ...     namespace="production",
        ...     rules=[
        ...         PolicyRule(api_groups=[""], resources=["pods"], verbs=["get", "list", "watch"]),
        ...     ],
        ... )
        >>> role = build_role(spec)
    """
    return ResourceBuilder.build(
        spec,
        "rbac.authorization.k8s.io/v1",
        "Role",
        include_spec=False,
        top_level_fields={"rules"},
    )


def build_clusterrole(spec: ClusterRoleSpec) -> dict:
    """Build a Kubernetes ClusterRole resource.

    Args:
        spec: ClusterRole specification

    Returns:
        Kubernetes ClusterRole resource as a dict

    Example:
        >>> from k8smith.core.models import ClusterRoleSpec, PolicyRule
        >>> spec = ClusterRoleSpec(
        ...     name="node-reader",
        ...     rules=[
        ...         PolicyRule(
        ...             api_groups=[""],
        ...             resources=["nodes"],
        ...             verbs=["get", "list", "watch"],
        ...         ),
        ...     ],
        ... )
        >>> cluster_role = build_clusterrole(spec)
    """
    return ResourceBuilder.build(
        spec,
        "rbac.authorization.k8s.io/v1",
        "ClusterRole",
        include_spec=False,
        top_level_fields={"rules", "aggregation_rule"},
    )


def build_rolebinding(spec: RoleBindingSpec) -> dict:
    """Build a Kubernetes RoleBinding resource.

    Args:
        spec: RoleBinding specification

    Returns:
        Kubernetes RoleBinding resource as a dict

    Example:
        >>> from k8smith.core.models import RoleBindingSpec, RoleBindingSubject, RoleRef
        >>> spec = RoleBindingSpec(
        ...     name="read-pods",
        ...     namespace="production",
        ...     subjects=[
        ...         RoleBindingSubject(kind="ServiceAccount", name="my-sa", namespace="production"),
        ...     ],
        ...     role_ref=RoleRef(kind="Role", name="pod-reader"),
        ... )
        >>> binding = build_rolebinding(spec)
    """
    return ResourceBuilder.build(
        spec,
        "rbac.authorization.k8s.io/v1",
        "RoleBinding",
        include_spec=False,
        top_level_fields={"role_ref", "subjects"},
    )


def build_clusterrolebinding(spec: ClusterRoleBindingSpec) -> dict:
    """Build a Kubernetes ClusterRoleBinding resource.

    Args:
        spec: ClusterRoleBinding specification

    Returns:
        Kubernetes ClusterRoleBinding resource as a dict

    Example:
        >>> from k8smith.core.models import ClusterRoleBindingSpec, RoleBindingSubject, RoleRef
        >>> spec = ClusterRoleBindingSpec(
        ...     name="read-nodes-global",
        ...     subjects=[
        ...         RoleBindingSubject(
        ...             kind="ServiceAccount",
        ...             name="monitoring",
        ...             namespace="kube-system",
        ...         ),
        ...     ],
        ...     role_ref=RoleRef(kind="ClusterRole", name="node-reader"),
        ... )
        >>> binding = build_clusterrolebinding(spec)
    """
    return ResourceBuilder.build(
        spec,
        "rbac.authorization.k8s.io/v1",
        "ClusterRoleBinding",
        include_spec=False,
        top_level_fields={"role_ref", "subjects"},
    )
