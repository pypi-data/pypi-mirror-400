"""Manifest collection and management."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from k8smith.output.yaml import dump, load


@dataclass
class Manifest:
    """A collection of Kubernetes resources.

    Example:
        >>> manifest = Manifest()
        >>> manifest.add({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test"}})
        >>> manifest.add(build_deployment(spec))
        >>> print(manifest.to_yaml())
        >>> manifest.write("manifests/app.yaml")
    """

    resources: list[dict] = field(default_factory=list)

    def add(self, resource: dict) -> Manifest:
        """Add a resource to the manifest.

        Args:
            resource: A Kubernetes resource dict

        Returns:
            Self for chaining
        """
        self.resources.append(resource)
        return self

    def add_all(self, resources: list[dict]) -> Manifest:
        """Add multiple resources to the manifest.

        Args:
            resources: List of Kubernetes resource dicts

        Returns:
            Self for chaining
        """
        self.resources.extend(resources)
        return self

    def to_yaml(self) -> str:
        """Serialize to YAML string.

        Returns:
            YAML string with --- document separators
        """
        return dump(self.resources)

    def write(self, path: str | Path) -> None:
        """Write manifest to a file.

        Args:
            path: File path to write to
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_yaml())

    @classmethod
    def from_yaml(cls, yaml_str: str) -> Manifest:
        """Load manifest from a YAML string.

        Args:
            yaml_str: YAML string with one or more documents

        Returns:
            Manifest containing the loaded resources
        """
        return cls(resources=load(yaml_str))

    @classmethod
    def from_file(cls, path: str | Path) -> Manifest:
        """Load manifest from a file.

        Args:
            path: Path to YAML file

        Returns:
            Manifest containing the loaded resources
        """
        path = Path(path)
        return cls.from_yaml(path.read_text())

    def filter(
        self,
        *,
        kind: str | None = None,
        namespace: str | None = None,
        name: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> Manifest:
        """Filter resources by criteria.

        Args:
            kind: Filter by resource kind (e.g., "Deployment")
            namespace: Filter by namespace
            name: Filter by resource name
            labels: Filter by labels (all must match)

        Returns:
            New Manifest with filtered resources
        """
        filtered = []
        for r in self.resources:
            if kind and r.get("kind") != kind:
                continue
            if namespace and r.get("metadata", {}).get("namespace") != namespace:
                continue
            if name and r.get("metadata", {}).get("name") != name:
                continue
            if labels:
                resource_labels = r.get("metadata", {}).get("labels", {})
                if not all(resource_labels.get(k) == v for k, v in labels.items()):
                    continue
            filtered.append(r)
        return Manifest(resources=filtered)

    def __len__(self) -> int:
        """Return the number of resources in the manifest."""
        return len(self.resources)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate over resources."""
        return iter(self.resources)

    def __getitem__(self, index: int) -> dict:
        """Get a resource by index."""
        return self.resources[index]
