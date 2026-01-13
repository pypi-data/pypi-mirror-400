"""Tests for validation module."""

from __future__ import annotations

import warnings

import pytest

from k8smith import (
    Container,
    DeploymentSpec,
    PodSpec,
    PodTemplateSpec,
    ResourceQuantity,
    ResourceRequirements,
    ValidationError,
    ValidationMode,
    build_deployment,
    validate_manifest,
)


class TestValidationModes:
    """Test validation mode behavior."""

    def test_none_mode_silent(self):
        """NONE mode should not emit warnings or raise exceptions."""
        # Missing namespace - structural error
        manifest = {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": "test"}}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = validate_manifest(manifest, structural=ValidationMode.NONE)

        assert len(w) == 0  # No warnings
        assert len(result) == 0  # No issues collected in NONE mode

    def test_check_mode_emits_warnings(self):
        """CHECK mode should emit warnings but not raise."""
        manifest = {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": "test"}}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_manifest(manifest, structural=ValidationMode.CHECK)

        assert len(w) > 0  # Warnings emitted
        assert any("namespace" in str(warning.message) for warning in w)

    def test_strict_mode_raises_exception(self):
        """STRICT mode should raise ValidationError."""
        manifest = {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": "test"}}

        with pytest.raises(ValidationError) as exc_info:
            validate_manifest(manifest, structural=ValidationMode.STRICT)

        assert len(exc_info.value.issues) > 0
        assert any("namespace" in i.path for i in exc_info.value.issues)


class TestStructuralValidation:
    """Test structural validation."""

    def test_valid_deployment_passes(self):
        """A valid deployment should pass structural validation."""
        spec = DeploymentSpec(
            name="test",
            namespace="default",
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="app", image="nginx:1.25")])
            ),
        )
        manifest = build_deployment(spec)

        result = validate_manifest(manifest, structural=ValidationMode.STRICT)
        assert len(result.errors) == 0

    def test_missing_api_version(self):
        """Missing apiVersion should be an error."""
        manifest = {"kind": "Deployment", "metadata": {"name": "test", "namespace": "default"}}

        with pytest.raises(ValidationError) as exc_info:
            validate_manifest(manifest, structural=ValidationMode.STRICT)

        assert any("apiVersion" in i.path for i in exc_info.value.issues)

    def test_missing_kind(self):
        """Missing kind should be an error."""
        manifest = {"apiVersion": "apps/v1", "metadata": {"name": "test", "namespace": "default"}}

        with pytest.raises(ValidationError) as exc_info:
            validate_manifest(manifest, structural=ValidationMode.STRICT)

        assert any("kind" in i.path for i in exc_info.value.issues)

    def test_missing_metadata_name(self):
        """Missing metadata.name should be an error."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"namespace": "default"},
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_manifest(manifest, structural=ValidationMode.STRICT)

        assert any("metadata.name" in i.path for i in exc_info.value.issues)

    def test_missing_containers(self):
        """Missing containers should be an error."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "test", "namespace": "default"},
            "spec": {
                "selector": {"matchLabels": {"app": "test"}},
                "template": {"metadata": {"labels": {"app": "test"}}, "spec": {}},
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_manifest(manifest, structural=ValidationMode.STRICT)

        assert any("containers" in i.path for i in exc_info.value.issues)

    def test_namespace_not_required_for_namespace_resource(self):
        """Namespace resource doesn't require metadata.namespace."""
        manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {"name": "test"},
        }

        # Should not raise
        result = validate_manifest(manifest, structural=ValidationMode.STRICT)
        assert len(result.errors) == 0


class TestCrossReferenceValidation:
    """Test cross-reference validation."""

    def test_volume_mount_references_existing_volume(self):
        """Volume mounts referencing existing volumes should pass."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "test", "namespace": "default"},
            "spec": {
                "selector": {"matchLabels": {"app": "test"}},
                "template": {
                    "metadata": {"labels": {"app": "test"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "app",
                                "image": "nginx",
                                "volumeMounts": [{"name": "config", "mountPath": "/etc/config"}],
                            }
                        ],
                        "volumes": [{"name": "config", "configMap": {"name": "my-config"}}],
                    },
                },
            },
        }

        result = validate_manifest(manifest, cross_reference=ValidationMode.STRICT)
        cross_ref_errors = [i for i in result.errors if i.category == "cross_reference"]
        assert len(cross_ref_errors) == 0

    def test_volume_mount_missing_volume(self):
        """Volume mount referencing non-existent volume should error."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "test", "namespace": "default"},
            "spec": {
                "selector": {"matchLabels": {"app": "test"}},
                "template": {
                    "metadata": {"labels": {"app": "test"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "app",
                                "image": "nginx",
                                "volumeMounts": [{"name": "missing", "mountPath": "/data"}],
                            }
                        ],
                    },
                },
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_manifest(manifest, cross_reference=ValidationMode.STRICT)

        assert any("missing" in i.message for i in exc_info.value.issues)

    def test_selector_matches_pod_labels(self):
        """Selector matching pod labels should pass."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "test", "namespace": "default"},
            "spec": {
                "selector": {"matchLabels": {"app": "test"}},
                "template": {
                    "metadata": {"labels": {"app": "test"}},
                    "spec": {"containers": [{"name": "app", "image": "nginx"}]},
                },
            },
        }

        result = validate_manifest(manifest, cross_reference=ValidationMode.STRICT)
        cross_ref_errors = [i for i in result.errors if i.category == "cross_reference"]
        assert len(cross_ref_errors) == 0

    def test_selector_missing_from_pod_labels(self):
        """Selector label missing from pod labels should error."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "test", "namespace": "default"},
            "spec": {
                "selector": {"matchLabels": {"app": "test", "version": "v1"}},
                "template": {
                    "metadata": {"labels": {"app": "test"}},  # Missing version
                    "spec": {"containers": [{"name": "app", "image": "nginx"}]},
                },
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_manifest(manifest, cross_reference=ValidationMode.STRICT)

        assert any("version" in i.message for i in exc_info.value.issues)

    def test_duplicate_port_names(self):
        """Duplicate port names should error."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "test", "namespace": "default"},
            "spec": {
                "selector": {"matchLabels": {"app": "test"}},
                "template": {
                    "metadata": {"labels": {"app": "test"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "app",
                                "image": "nginx",
                                "ports": [{"name": "http", "containerPort": 80}],
                            },
                            {
                                "name": "sidecar",
                                "image": "proxy",
                                "ports": [{"name": "http", "containerPort": 8080}],
                            },
                        ]
                    },
                },
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_manifest(manifest, cross_reference=ValidationMode.STRICT)

        assert any(
            "http" in i.message and "already used" in i.message for i in exc_info.value.issues
        )


class TestBestPracticeValidation:
    """Test best practice validation."""

    def test_missing_resources_warning(self):
        """Missing resources should emit warning."""
        spec = DeploymentSpec(
            name="test",
            namespace="default",
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="app", image="nginx:1.25")])
            ),
        )
        manifest = build_deployment(spec)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_manifest(manifest, best_practice=ValidationMode.CHECK)

        assert any("resource" in str(warning.message).lower() for warning in w)

    def test_with_resources_no_resource_warning(self):
        """Containers with resources should not warn about missing resources."""
        spec = DeploymentSpec(
            name="test",
            namespace="default",
            template=PodTemplateSpec(
                spec=PodSpec(
                    containers=[
                        Container(
                            name="app",
                            image="nginx:1.25",
                            resources=ResourceRequirements(
                                requests=ResourceQuantity(cpu="100m", memory="128Mi"),
                                limits=ResourceQuantity(memory="256Mi"),
                            ),
                        )
                    ]
                )
            ),
        )
        manifest = build_deployment(spec)

        # Capture warnings to prevent them from leaking to pytest output
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = validate_manifest(manifest, best_practice=ValidationMode.CHECK)

        resource_warnings = [i for i in result.warnings if "no resource" in i.message.lower()]
        assert len(resource_warnings) == 0

    def test_latest_tag_warning(self):
        """Using :latest tag should emit warning."""
        spec = DeploymentSpec(
            name="test",
            namespace="default",
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="app", image="nginx:latest")])
            ),
        )
        manifest = build_deployment(spec)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_manifest(manifest, best_practice=ValidationMode.CHECK)

        assert any("latest" in str(warning.message) for warning in w)

    def test_no_tag_warning(self):
        """Image without tag should emit warning."""
        spec = DeploymentSpec(
            name="test",
            namespace="default",
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="app", image="nginx")])
            ),
        )
        manifest = build_deployment(spec)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_manifest(manifest, best_practice=ValidationMode.CHECK)

        assert any("latest" in str(warning.message) for warning in w)

    def test_missing_probes_warning(self):
        """Missing probes should emit warning."""
        spec = DeploymentSpec(
            name="test",
            namespace="default",
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="app", image="nginx:1.25")])
            ),
        )
        manifest = build_deployment(spec)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_manifest(manifest, best_practice=ValidationMode.CHECK)

        warning_messages = [str(warning.message) for warning in w]
        assert any("readiness" in msg.lower() for msg in warning_messages)
        assert any("liveness" in msg.lower() for msg in warning_messages)


class TestValidationResult:
    """Test ValidationResult behavior."""

    def test_bool_empty_result(self):
        """Empty result should be falsy."""
        from k8smith.validation import ValidationResult

        result = ValidationResult()
        assert not result

    def test_bool_with_issues(self):
        """Result with issues should be truthy."""
        from k8smith.validation import ValidationResult

        result = ValidationResult()
        result.error("path", "message", "structural")
        assert result

    def test_iteration(self):
        """Should be iterable."""
        from k8smith.validation import ValidationResult

        result = ValidationResult()
        result.error("path1", "msg1", "structural")
        result.warning("path2", "msg2", "best_practice")

        issues = list(result)
        assert len(issues) == 2

    def test_errors_property(self):
        """errors property should filter to errors only."""
        from k8smith.validation import ValidationResult

        result = ValidationResult()
        result.error("path1", "msg1", "structural")
        result.warning("path2", "msg2", "best_practice")

        assert len(result.errors) == 1
        assert len(result.warnings) == 1
