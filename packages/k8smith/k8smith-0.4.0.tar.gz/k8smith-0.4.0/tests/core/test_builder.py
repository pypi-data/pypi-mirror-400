"""Tests for ResourceBuilder."""

from pydantic import Field

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import KubeModel


class SimpleSpec(KubeModel):
    """Simple spec for testing."""

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    replicas: int | None = None
    some_field: str | None = Field(default=None, alias="someField")


class NestedModel(KubeModel):
    """Nested model for testing."""

    value: str
    count: int | None = None


class SpecWithNested(KubeModel):
    """Spec with nested models for testing."""

    name: str
    namespace: str
    nested: NestedModel | None = None
    nested_list: list[NestedModel] | None = Field(default=None, alias="nestedList")


class TestResourceBuilder:
    """Tests for ResourceBuilder.build method."""

    def test_basic_resource(self):
        """Test building a basic resource with metadata and spec."""
        spec = SimpleSpec(name="test", namespace="default", replicas=3)

        result = ResourceBuilder.build(spec, "apps/v1", "Deployment")

        assert result["apiVersion"] == "apps/v1"
        assert result["kind"] == "Deployment"
        assert result["metadata"]["name"] == "test"
        assert result["metadata"]["namespace"] == "default"
        assert result["spec"]["replicas"] == 3

    def test_field_alias(self):
        """Test that field aliases are used in output."""
        spec = SimpleSpec(name="test", namespace="default", some_field="value")

        result = ResourceBuilder.build(spec, "v1", "Test")

        assert result["spec"]["someField"] == "value"
        assert "some_field" not in result["spec"]

    def test_labels_and_annotations(self):
        """Test that labels and annotations go to metadata."""
        spec = SimpleSpec(
            name="test",
            namespace="default",
            labels={"app": "web"},
            annotations={"note": "test"},
        )

        result = ResourceBuilder.build(spec, "v1", "Test")

        assert result["metadata"]["labels"] == {"app": "web"}
        assert result["metadata"]["annotations"] == {"note": "test"}

    def test_empty_labels_not_included(self):
        """Test that empty labels/annotations are not included."""
        spec = SimpleSpec(name="test", namespace="default", labels={}, annotations={})

        result = ResourceBuilder.build(spec, "v1", "Test")

        assert "labels" not in result["metadata"]
        assert "annotations" not in result["metadata"]

    def test_none_values_not_included(self):
        """Test that None values are not included in output."""
        spec = SimpleSpec(name="test", namespace="default")

        result = ResourceBuilder.build(spec, "v1", "Test")

        assert "replicas" not in result["spec"]
        assert "someField" not in result["spec"]

    def test_include_spec_false(self):
        """Test building a resource without spec section (like Namespace)."""
        spec = SimpleSpec(name="test", namespace="default", labels={"env": "prod"})

        result = ResourceBuilder.build(spec, "v1", "Namespace", include_spec=False)

        assert "spec" not in result
        assert result["metadata"]["name"] == "test"
        assert result["metadata"]["labels"] == {"env": "prod"}

    def test_top_level_fields(self):
        """Test that top_level_fields go to resource root."""
        spec = SimpleSpec(name="test", namespace="default", replicas=3)

        result = ResourceBuilder.build(spec, "v1", "Test", top_level_fields={"replicas"})

        assert result["replicas"] == 3
        assert "replicas" not in result["spec"]

    def test_skip_fields(self):
        """Test that skip_fields are not included in output."""
        spec = SimpleSpec(name="test", namespace="default", replicas=3, some_field="x")

        result = ResourceBuilder.build(spec, "v1", "Test", skip_fields={"replicas", "some_field"})

        assert "replicas" not in result["spec"]
        assert "someField" not in result["spec"]

    def test_nested_model_transformed(self):
        """Test that nested KubeModel is transformed to dict."""
        spec = SpecWithNested(
            name="test", namespace="default", nested=NestedModel(value="hello", count=5)
        )

        result = ResourceBuilder.build(spec, "v1", "Test")

        assert result["spec"]["nested"] == {"value": "hello", "count": 5}

    def test_nested_list_transformed(self):
        """Test that list of KubeModels is transformed to list of dicts."""
        spec = SpecWithNested(
            name="test",
            namespace="default",
            nested_list=[NestedModel(value="a"), NestedModel(value="b", count=2)],
        )

        result = ResourceBuilder.build(spec, "v1", "Test")

        assert result["spec"]["nestedList"] == [{"value": "a"}, {"value": "b", "count": 2}]

    def test_combined_options(self):
        """Test combining multiple options."""
        spec = SimpleSpec(
            name="test",
            namespace="default",
            labels={"app": "test"},
            replicas=5,
            some_field="value",
        )

        result = ResourceBuilder.build(
            spec,
            "v1",
            "Test",
            top_level_fields={"replicas"},
            skip_fields={"some_field"},
        )

        assert result["replicas"] == 5
        assert "replicas" not in result["spec"]
        assert "someField" not in result["spec"]
        assert result["metadata"]["labels"] == {"app": "test"}
