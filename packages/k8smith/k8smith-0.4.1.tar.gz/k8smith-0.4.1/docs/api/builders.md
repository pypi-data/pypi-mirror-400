# Core Builders

Builder functions that convert spec models into Kubernetes manifest dictionaries.

## Custom Resources

Use `ResourceBuilder` to create builders for custom Kubernetes resources (CRDs, operators, etc.).

### How It Works

ResourceBuilder automatically:

- Routes `name`, `namespace`, `labels`, `annotations` to `metadata`
- Routes other fields to `spec` (or top-level for special resources)
- Transforms nested `KubeModel` instances to dicts via `.to_dict()`
- Uses Pydantic field aliases for camelCase output

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spec` | required | The specification model instance |
| `api_version` | required | Kubernetes API version (e.g., `"v1"`, `"apps/v1"`) |
| `kind` | required | Resource kind (e.g., `"Service"`, `"Deployment"`) |
| `include_spec` | `True` | Set `False` for resources without a spec section (Namespace, ConfigMap, RBAC) |
| `top_level_fields` | `None` | Field names placed at resource root instead of spec (e.g., `{"rules"}` for Role) |
| `skip_fields` | `None` | Field names to skip (for manual handling) |

### Basic Example

```python
from k8smith import ResourceBuilder, KubeModel
from pydantic import Field

class MyCustomSpec(KubeModel):
    name: str
    namespace: str = "default"
    replicas: int = 1
    custom_field: str = Field(alias="customField")

def build_my_resource(spec: MyCustomSpec) -> dict:
    return ResourceBuilder.build(spec, "example.com/v1", "MyResource")

# Usage
spec = MyCustomSpec(name="my-app", custom_field="value")
manifest = build_my_resource(spec)
```

### Advanced: Resources Without spec Section

Some Kubernetes resources (Namespace, ConfigMap, RBAC) don't have a `spec` section:

```python
def build_my_config(spec: MyConfigSpec) -> dict:
    return ResourceBuilder.build(
        spec, "v1", "ConfigMap",
        include_spec=False,
        top_level_fields={"data"},
    )
```

::: k8smith.core.builder.ResourceBuilder

## Workloads

::: k8smith.core.deployment.build_deployment

::: k8smith.core.statefulset.build_statefulset

::: k8smith.core.daemonset.build_daemonset

::: k8smith.core.cronjob.build_cronjob

## Services

::: k8smith.core.service.build_service

## Configuration

::: k8smith.core.configmap.build_configmap

::: k8smith.core.secret.build_secret

## Scaling & Availability

::: k8smith.core.hpa.build_hpa

::: k8smith.core.pdb.build_pdb

## Identity

::: k8smith.core.serviceaccount.build_serviceaccount

::: k8smith.core.namespace.build_namespace

## RBAC

::: k8smith.core.rbac.build_role

::: k8smith.core.rbac.build_clusterrole

::: k8smith.core.rbac.build_rolebinding

::: k8smith.core.rbac.build_clusterrolebinding
