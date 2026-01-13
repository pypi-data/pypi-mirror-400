"""Tests for YAML output utilities."""

from k8smith.output.manifest import Manifest
from k8smith.output.yaml import dump, dump_one, load


class TestYamlDump:
    """Tests for YAML dump functions."""

    def test_dump_single_resource(self):
        """Test dumping a single resource."""
        resource = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {"name": "test"},
        }

        result = dump([resource])

        assert "apiVersion: v1" in result
        assert "kind: Namespace" in result
        assert "name: test" in result

    def test_dump_multiple_resources(self):
        """Test dumping multiple resources with separators."""
        resources = [
            {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test1"}},
            {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test2"}},
        ]

        result = dump(resources)

        assert "---" in result
        assert "name: test1" in result
        assert "name: test2" in result

    def test_dump_one(self):
        """Test dumping a single resource without separator."""
        resource = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test"}}

        result = dump_one(resource)

        assert "---" not in result
        assert "apiVersion: v1" in result

    def test_load_single_document(self):
        """Test loading a single YAML document."""
        yaml_str = "apiVersion: v1\nkind: Namespace\nmetadata:\n  name: test"

        result = load(yaml_str)

        assert len(result) == 1
        assert result[0]["kind"] == "Namespace"

    def test_load_multiple_documents(self):
        """Test loading multiple YAML documents."""
        yaml_str = """apiVersion: v1
kind: Namespace
metadata:
  name: test1
---
apiVersion: v1
kind: Namespace
metadata:
  name: test2
"""
        result = load(yaml_str)

        assert len(result) == 2
        assert result[0]["metadata"]["name"] == "test1"
        assert result[1]["metadata"]["name"] == "test2"


class TestManifest:
    """Tests for Manifest class."""

    def test_add_resource(self):
        """Test adding a resource to manifest."""
        manifest = Manifest()
        resource = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test"}}

        manifest.add(resource)

        assert len(manifest) == 1
        assert manifest[0]["kind"] == "Namespace"

    def test_add_all_resources(self):
        """Test adding multiple resources."""
        manifest = Manifest()
        resources = [
            {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test1"}},
            {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test2"}},
        ]

        manifest.add_all(resources)

        assert len(manifest) == 2

    def test_filter_by_kind(self):
        """Test filtering resources by kind."""
        manifest = Manifest()
        manifest.add({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test"}})
        manifest.add(
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "web", "namespace": "test"},
            }
        )

        filtered = manifest.filter(kind="Deployment")

        assert len(filtered) == 1
        assert filtered[0]["kind"] == "Deployment"

    def test_filter_by_namespace(self):
        """Test filtering resources by namespace."""
        manifest = Manifest()
        manifest.add(
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "web", "namespace": "prod"},
            }
        )
        manifest.add(
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "api", "namespace": "staging"},
            }
        )

        filtered = manifest.filter(namespace="prod")

        assert len(filtered) == 1
        assert filtered[0]["metadata"]["name"] == "web"

    def test_to_yaml(self):
        """Test converting manifest to YAML."""
        manifest = Manifest()
        manifest.add({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test"}})

        yaml_str = manifest.to_yaml()

        assert "apiVersion: v1" in yaml_str
        assert "kind: Namespace" in yaml_str

    def test_iteration(self):
        """Test iterating over manifest resources."""
        manifest = Manifest()
        manifest.add({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test1"}})
        manifest.add({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test2"}})

        names = [r["metadata"]["name"] for r in manifest]

        assert names == ["test1", "test2"]

    def test_chaining(self):
        """Test method chaining."""
        manifest = (
            Manifest()
            .add({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test1"}})
            .add({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test2"}})
        )

        assert len(manifest) == 2
