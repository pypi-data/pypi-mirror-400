"""RBAC resource builders.

Provides builders for Role, ClusterRole, RoleBinding, and ClusterRoleBinding resources.
"""

from __future__ import annotations

from k8smith.core.models import (
    ClusterRoleBindingSpec,
    ClusterRoleSpec,
    PolicyRule,
    RoleBindingSpec,
    RoleBindingSubject,
    RoleRef,
    RoleSpec,
)


def _build_rule(rule: PolicyRule) -> dict:
    """Build a policy rule dict."""
    result: dict = {"verbs": rule.verbs}

    if rule.api_groups is not None:
        result["apiGroups"] = rule.api_groups
    if rule.resources:
        result["resources"] = rule.resources
    if rule.resource_names:
        result["resourceNames"] = rule.resource_names
    if rule.non_resource_urls:
        result["nonResourceURLs"] = rule.non_resource_urls

    return result


def _build_subject(subject: RoleBindingSubject) -> dict:
    """Build a subject dict."""
    result: dict = {
        "kind": subject.kind,
        "name": subject.name,
    }

    if subject.namespace:
        result["namespace"] = subject.namespace
    if subject.api_group:
        result["apiGroup"] = subject.api_group

    return result


def _build_role_ref(role_ref: RoleRef) -> dict:
    """Build a roleRef dict."""
    return {
        "apiGroup": role_ref.api_group,
        "kind": role_ref.kind,
        "name": role_ref.name,
    }


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
    role: dict = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "Role",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        role["metadata"]["labels"] = spec.labels
    if spec.annotations:
        role["metadata"]["annotations"] = spec.annotations

    # Add rules
    if spec.rules:
        role["rules"] = [_build_rule(rule) for rule in spec.rules]

    return role


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
    cluster_role: dict = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "ClusterRole",
        "metadata": {
            "name": spec.name,
        },
    }

    # Add optional metadata fields
    if spec.labels:
        cluster_role["metadata"]["labels"] = spec.labels
    if spec.annotations:
        cluster_role["metadata"]["annotations"] = spec.annotations

    # Add rules
    if spec.rules:
        cluster_role["rules"] = [_build_rule(rule) for rule in spec.rules]

    # Add aggregation rule (for aggregated ClusterRoles)
    if spec.aggregation_rule:
        cluster_role["aggregationRule"] = spec.aggregation_rule

    return cluster_role


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
    binding: dict = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "RoleBinding",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "roleRef": _build_role_ref(spec.role_ref),
    }

    # Add optional metadata fields
    if spec.labels:
        binding["metadata"]["labels"] = spec.labels
    if spec.annotations:
        binding["metadata"]["annotations"] = spec.annotations

    # Add subjects
    if spec.subjects:
        binding["subjects"] = [_build_subject(subj) for subj in spec.subjects]

    return binding


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
    binding: dict = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "ClusterRoleBinding",
        "metadata": {
            "name": spec.name,
        },
        "roleRef": _build_role_ref(spec.role_ref),
    }

    # Add optional metadata fields
    if spec.labels:
        binding["metadata"]["labels"] = spec.labels
    if spec.annotations:
        binding["metadata"]["annotations"] = spec.annotations

    # Add subjects
    if spec.subjects:
        binding["subjects"] = [_build_subject(subj) for subj in spec.subjects]

    return binding
