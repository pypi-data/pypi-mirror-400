"""YAML serialization utilities for Kubernetes manifests."""

import yaml


class KubernetesYamlDumper(yaml.SafeDumper):
    """Custom YAML dumper with Kubernetes-friendly formatting.

    - No aliases (no &id001, *id001)
    - None values are omitted
    - Multi-line strings use literal block style
    """

    pass


# Don't use aliases (e.g., &id001, *id001)
KubernetesYamlDumper.ignore_aliases = lambda self, data: True  # type: ignore[method-assign]


def _represent_none(dumper: KubernetesYamlDumper, _: None) -> yaml.Node:
    """Represent None as empty string."""
    return dumper.represent_scalar("tag:yaml.org,2002:null", "")


def _represent_str(dumper: KubernetesYamlDumper, data: str) -> yaml.Node:
    """Represent strings, using literal block style for multi-line."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


KubernetesYamlDumper.add_representer(type(None), _represent_none)
KubernetesYamlDumper.add_representer(str, _represent_str)


def dump(resources: list[dict]) -> str:
    """Dump resources to a YAML string with document separators.

    Args:
        resources: List of Kubernetes resource dicts

    Returns:
        YAML string with --- document separators

    Example:
        >>> resources = [{"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "test"}}]
        >>> print(dump(resources))
        apiVersion: v1
        kind: Namespace
        metadata:
          name: test
    """
    if not resources:
        return ""

    docs = []
    for resource in resources:
        doc = yaml.dump(
            resource,
            Dumper=KubernetesYamlDumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        docs.append(doc.rstrip())

    return "\n---\n".join(docs) + "\n"


def dump_one(resource: dict) -> str:
    """Dump a single resource to YAML.

    Args:
        resource: A Kubernetes resource dict

    Returns:
        YAML string
    """
    return yaml.dump(
        resource,
        Dumper=KubernetesYamlDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )


def load(yaml_str: str) -> list[dict]:
    """Load resources from a YAML string.

    Args:
        yaml_str: YAML string (may contain multiple documents separated by ---)

    Returns:
        List of resource dicts
    """
    return [doc for doc in yaml.safe_load_all(yaml_str) if doc]
