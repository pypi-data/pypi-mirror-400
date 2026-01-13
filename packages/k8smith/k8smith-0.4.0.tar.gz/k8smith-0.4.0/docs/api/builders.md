# Core Builders

Builder functions that convert spec models into Kubernetes manifest dictionaries.

## Custom Resources

Use `ResourceBuilder` to create builders for custom Kubernetes resources:

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
