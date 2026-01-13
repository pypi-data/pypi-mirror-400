# k8smith

A transparent, lightweight Kubernetes manifest generator.

## Philosophy

- **Transparency over abstraction** — Generated YAML is predictable; no hidden defaults
- **Composition over inheritance** — Build complex resources from simple pieces
- **Type safety at the boundary** — Validate inputs with Pydantic, output plain dicts
- **Cloud-agnostic core** — Vanilla K8s resources work anywhere; cloud extensions are optional

## Installation

```bash
pip install k8smith
# or
uv add k8smith
```

## Quick Example

```python
from k8smith import (
    DeploymentSpec,
    Container,
    PodSpec,
    PodTemplateSpec,
    ResourceRequirements,
    ResourceQuantity,
    build_deployment,
    Manifest,
)

spec = DeploymentSpec(
    name="web",
    namespace="production",
    replicas=3,
    template=PodTemplateSpec(
        spec=PodSpec(
            containers=[
                Container(
                    name="web",
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

deployment = build_deployment(spec)

manifest = Manifest()
manifest.add(deployment)
print(manifest.to_yaml())
```

## Why not cdk8s?

k8smith was created to replace cdk8s after encountering these issues:

| cdk8s Problem | k8smith Solution |
|---------------|-------------------|
| `Size.gibibytes(6)` outputs `6144Mi` | Strings stay as strings: `"6Gi"` |
| Can't add `nvidia.com/gpu` via resources | Built into `ResourceQuantity.extended` |
| Adds `hostNetwork: false` when not set | Only outputs what you specify |
| Requires label cleanup post-processing | No generated labels |
| JSII/Node.js dependency | Pure Python |

## Next Steps

- [Getting Started](getting-started.md) — Installation and basic usage
- [Production Web App Guide](guides/web-app.md) — Complete example with all best practices
- [API Reference](api/models.md) — Full API documentation
