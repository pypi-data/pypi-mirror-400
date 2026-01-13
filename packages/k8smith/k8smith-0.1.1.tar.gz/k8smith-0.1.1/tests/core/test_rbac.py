"""Tests for RBAC resource builders."""

from k8smith import (
    ClusterRoleBindingSpec,
    ClusterRoleSpec,
    PolicyRule,
    RoleBindingSpec,
    RoleBindingSubject,
    RoleRef,
    RoleSpec,
    build_clusterrole,
    build_clusterrolebinding,
    build_role,
    build_rolebinding,
)


class TestBuildRole:
    """Tests for build_role function."""

    def test_minimal_role(self):
        """Test building a minimal Role."""
        spec = RoleSpec(
            name="pod-reader",
            namespace="default",
        )

        result = build_role(spec)

        assert result["apiVersion"] == "rbac.authorization.k8s.io/v1"
        assert result["kind"] == "Role"
        assert result["metadata"]["name"] == "pod-reader"
        assert result["metadata"]["namespace"] == "default"
        assert "rules" not in result

    def test_role_with_rules(self):
        """Test Role with policy rules."""
        spec = RoleSpec(
            name="pod-reader",
            namespace="production",
            rules=[
                PolicyRule(
                    api_groups=[""],
                    resources=["pods", "pods/log"],
                    verbs=["get", "list", "watch"],
                ),
                PolicyRule(
                    api_groups=["apps"],
                    resources=["deployments"],
                    verbs=["get", "list"],
                ),
            ],
        )

        result = build_role(spec)

        assert len(result["rules"]) == 2
        assert result["rules"][0]["apiGroups"] == [""]
        assert result["rules"][0]["resources"] == ["pods", "pods/log"]
        assert result["rules"][0]["verbs"] == ["get", "list", "watch"]
        assert result["rules"][1]["apiGroups"] == ["apps"]

    def test_role_with_resource_names(self):
        """Test Role targeting specific resource names."""
        spec = RoleSpec(
            name="specific-deployment-viewer",
            namespace="production",
            rules=[
                PolicyRule(
                    api_groups=["apps"],
                    resources=["deployments"],
                    resource_names=["my-app", "my-other-app"],
                    verbs=["get", "watch"],
                ),
            ],
        )

        result = build_role(spec)

        assert result["rules"][0]["resourceNames"] == ["my-app", "my-other-app"]

    def test_role_with_labels_and_annotations(self):
        """Test Role with metadata labels and annotations."""
        spec = RoleSpec(
            name="pod-reader",
            namespace="default",
            labels={"team": "platform", "managed-by": "k8smith"},
            annotations={"description": "Read-only access to pods"},
        )

        result = build_role(spec)

        assert result["metadata"]["labels"]["team"] == "platform"
        assert result["metadata"]["annotations"]["description"] == "Read-only access to pods"

    def test_role_no_extra_fields(self):
        """Ensure no unexpected fields are included."""
        spec = RoleSpec(
            name="test-role",
            namespace="default",
            rules=[PolicyRule(verbs=["get"])],
        )

        result = build_role(spec)

        assert "labels" not in result["metadata"]
        assert "annotations" not in result["metadata"]


class TestBuildClusterRole:
    """Tests for build_clusterrole function."""

    def test_minimal_clusterrole(self):
        """Test building a minimal ClusterRole."""
        spec = ClusterRoleSpec(name="node-reader")

        result = build_clusterrole(spec)

        assert result["apiVersion"] == "rbac.authorization.k8s.io/v1"
        assert result["kind"] == "ClusterRole"
        assert result["metadata"]["name"] == "node-reader"
        assert "namespace" not in result["metadata"]

    def test_clusterrole_with_rules(self):
        """Test ClusterRole with policy rules."""
        spec = ClusterRoleSpec(
            name="node-reader",
            rules=[
                PolicyRule(
                    api_groups=[""],
                    resources=["nodes"],
                    verbs=["get", "list", "watch"],
                ),
            ],
        )

        result = build_clusterrole(spec)

        assert len(result["rules"]) == 1
        assert result["rules"][0]["resources"] == ["nodes"]

    def test_clusterrole_with_non_resource_urls(self):
        """Test ClusterRole with non-resource URLs."""
        spec = ClusterRoleSpec(
            name="health-reader",
            rules=[
                PolicyRule(
                    non_resource_urls=["/healthz", "/healthz/*"],
                    verbs=["get"],
                ),
            ],
        )

        result = build_clusterrole(spec)

        assert result["rules"][0]["nonResourceURLs"] == ["/healthz", "/healthz/*"]
        assert result["rules"][0]["verbs"] == ["get"]

    def test_clusterrole_with_aggregation_rule(self):
        """Test aggregated ClusterRole."""
        spec = ClusterRoleSpec(
            name="aggregate-reader",
            aggregation_rule={
                "clusterRoleSelectors": [
                    {"matchLabels": {"rbac.example.com/aggregate-to-reader": "true"}}
                ]
            },
        )

        result = build_clusterrole(spec)

        assert "aggregationRule" in result
        assert len(result["aggregationRule"]["clusterRoleSelectors"]) == 1

    def test_clusterrole_with_labels(self):
        """Test ClusterRole with labels."""
        spec = ClusterRoleSpec(
            name="node-reader",
            labels={"rbac.example.com/aggregate-to-admin": "true"},
        )

        result = build_clusterrole(spec)

        assert result["metadata"]["labels"]["rbac.example.com/aggregate-to-admin"] == "true"


class TestBuildRoleBinding:
    """Tests for build_rolebinding function."""

    def test_minimal_rolebinding(self):
        """Test building a minimal RoleBinding."""
        spec = RoleBindingSpec(
            name="read-pods",
            namespace="default",
            role_ref=RoleRef(kind="Role", name="pod-reader"),
        )

        result = build_rolebinding(spec)

        assert result["apiVersion"] == "rbac.authorization.k8s.io/v1"
        assert result["kind"] == "RoleBinding"
        assert result["metadata"]["name"] == "read-pods"
        assert result["metadata"]["namespace"] == "default"
        assert result["roleRef"]["apiGroup"] == "rbac.authorization.k8s.io"
        assert result["roleRef"]["kind"] == "Role"
        assert result["roleRef"]["name"] == "pod-reader"

    def test_rolebinding_with_serviceaccount_subject(self):
        """Test RoleBinding with ServiceAccount subject."""
        spec = RoleBindingSpec(
            name="read-pods",
            namespace="production",
            subjects=[
                RoleBindingSubject(
                    kind="ServiceAccount",
                    name="my-sa",
                    namespace="production",
                ),
            ],
            role_ref=RoleRef(kind="Role", name="pod-reader"),
        )

        result = build_rolebinding(spec)

        assert len(result["subjects"]) == 1
        assert result["subjects"][0]["kind"] == "ServiceAccount"
        assert result["subjects"][0]["name"] == "my-sa"
        assert result["subjects"][0]["namespace"] == "production"

    def test_rolebinding_with_user_subject(self):
        """Test RoleBinding with User subject."""
        spec = RoleBindingSpec(
            name="developer-pods",
            namespace="development",
            subjects=[
                RoleBindingSubject(
                    kind="User",
                    name="jane@example.com",
                    api_group="rbac.authorization.k8s.io",
                ),
            ],
            role_ref=RoleRef(kind="Role", name="pod-reader"),
        )

        result = build_rolebinding(spec)

        assert result["subjects"][0]["kind"] == "User"
        assert result["subjects"][0]["name"] == "jane@example.com"
        assert result["subjects"][0]["apiGroup"] == "rbac.authorization.k8s.io"

    def test_rolebinding_with_group_subject(self):
        """Test RoleBinding with Group subject."""
        spec = RoleBindingSpec(
            name="team-pods",
            namespace="production",
            subjects=[
                RoleBindingSubject(
                    kind="Group",
                    name="developers",
                    api_group="rbac.authorization.k8s.io",
                ),
            ],
            role_ref=RoleRef(kind="Role", name="pod-reader"),
        )

        result = build_rolebinding(spec)

        assert result["subjects"][0]["kind"] == "Group"
        assert result["subjects"][0]["name"] == "developers"

    def test_rolebinding_with_multiple_subjects(self):
        """Test RoleBinding with multiple subjects."""
        spec = RoleBindingSpec(
            name="multi-subject-binding",
            namespace="production",
            subjects=[
                RoleBindingSubject(kind="ServiceAccount", name="app-sa", namespace="production"),
                RoleBindingSubject(kind="User", name="admin@example.com"),
                RoleBindingSubject(kind="Group", name="ops-team"),
            ],
            role_ref=RoleRef(kind="Role", name="pod-admin"),
        )

        result = build_rolebinding(spec)

        assert len(result["subjects"]) == 3

    def test_rolebinding_referencing_clusterrole(self):
        """Test RoleBinding that references a ClusterRole."""
        spec = RoleBindingSpec(
            name="local-admin",
            namespace="production",
            subjects=[
                RoleBindingSubject(kind="ServiceAccount", name="admin-sa", namespace="production"),
            ],
            role_ref=RoleRef(kind="ClusterRole", name="admin"),
        )

        result = build_rolebinding(spec)

        assert result["roleRef"]["kind"] == "ClusterRole"
        assert result["roleRef"]["name"] == "admin"


class TestBuildClusterRoleBinding:
    """Tests for build_clusterrolebinding function."""

    def test_minimal_clusterrolebinding(self):
        """Test building a minimal ClusterRoleBinding."""
        spec = ClusterRoleBindingSpec(
            name="read-nodes-global",
            role_ref=RoleRef(kind="ClusterRole", name="node-reader"),
        )

        result = build_clusterrolebinding(spec)

        assert result["apiVersion"] == "rbac.authorization.k8s.io/v1"
        assert result["kind"] == "ClusterRoleBinding"
        assert result["metadata"]["name"] == "read-nodes-global"
        assert "namespace" not in result["metadata"]
        assert result["roleRef"]["kind"] == "ClusterRole"

    def test_clusterrolebinding_with_serviceaccount(self):
        """Test ClusterRoleBinding with ServiceAccount from specific namespace."""
        spec = ClusterRoleBindingSpec(
            name="monitoring-nodes",
            subjects=[
                RoleBindingSubject(
                    kind="ServiceAccount",
                    name="prometheus",
                    namespace="monitoring",
                ),
            ],
            role_ref=RoleRef(kind="ClusterRole", name="node-reader"),
        )

        result = build_clusterrolebinding(spec)

        assert result["subjects"][0]["namespace"] == "monitoring"

    def test_clusterrolebinding_with_labels(self):
        """Test ClusterRoleBinding with labels."""
        spec = ClusterRoleBindingSpec(
            name="admin-binding",
            labels={"managed-by": "k8smith"},
            annotations={"purpose": "grant admin access"},
            subjects=[
                RoleBindingSubject(kind="Group", name="cluster-admins"),
            ],
            role_ref=RoleRef(kind="ClusterRole", name="cluster-admin"),
        )

        result = build_clusterrolebinding(spec)

        assert result["metadata"]["labels"]["managed-by"] == "k8smith"
        assert result["metadata"]["annotations"]["purpose"] == "grant admin access"


class TestRoleRefDefaults:
    """Test default values for RoleRef."""

    def test_roleref_default_apigroup(self):
        """Test that RoleRef has correct default apiGroup."""
        role_ref = RoleRef(kind="Role", name="test-role")

        assert role_ref.api_group == "rbac.authorization.k8s.io"

    def test_roleref_in_binding(self):
        """Test RoleRef serialization in binding."""
        spec = RoleBindingSpec(
            name="test-binding",
            namespace="default",
            role_ref=RoleRef(kind="Role", name="test-role"),
        )

        result = build_rolebinding(spec)

        assert result["roleRef"]["apiGroup"] == "rbac.authorization.k8s.io"
