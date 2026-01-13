# Core Models

Pydantic models for Kubernetes resource specifications.

## Base Models

`KubeModel` is the base class for all specification models. Extend it to create custom resource specs:

```python
from k8smith import KubeModel, ResourceBuilder
from pydantic import Field

class MySpec(KubeModel):
    name: str
    namespace: str = "default"
    my_field: str = Field(alias="myField")  # outputs as camelCase
```

Key features:

- Excludes `None` values from output
- Supports Pydantic field aliases for camelCase keys
- Provides `.to_dict()` for nested model serialization

::: k8smith.core.models.KubeModel
    options:
      show_bases: false

## Resource Specifications

### Deployment

::: k8smith.core.models.DeploymentSpec

### StatefulSet

::: k8smith.core.models.StatefulSetSpec

### DaemonSet

::: k8smith.core.models.DaemonSetSpec

### Service

::: k8smith.core.models.ServiceSpec

### CronJob

::: k8smith.core.models.CronJobSpec

### ConfigMap

::: k8smith.core.models.ConfigMapSpec

### Secret

::: k8smith.core.models.SecretSpec

### HPA

::: k8smith.core.models.HPASpec

### PDB

::: k8smith.core.models.PDBSpec

### ServiceAccount

::: k8smith.core.models.ServiceAccountSpec

### Namespace

::: k8smith.core.models.NamespaceSpec

## RBAC Models

### Role

::: k8smith.core.models.RoleSpec

### ClusterRole

::: k8smith.core.models.ClusterRoleSpec

### RoleBinding

::: k8smith.core.models.RoleBindingSpec

### ClusterRoleBinding

::: k8smith.core.models.ClusterRoleBindingSpec

### PolicyRule

::: k8smith.core.models.PolicyRule

### RoleRef

::: k8smith.core.models.RoleRef

### RoleBindingSubject

::: k8smith.core.models.RoleBindingSubject

## Pod Components

### Container

::: k8smith.core.models.Container

### PodSpec

::: k8smith.core.models.PodSpec

### PodTemplateSpec

::: k8smith.core.models.PodTemplateSpec

### Volume

::: k8smith.core.models.Volume

### VolumeMount

::: k8smith.core.models.VolumeMount

### EnvVar

::: k8smith.core.models.EnvVar

### Probe

::: k8smith.core.models.Probe

### ResourceRequirements

::: k8smith.core.models.ResourceRequirements

### ResourceQuantity

::: k8smith.core.models.ResourceQuantity

## Security

### SecurityContext

::: k8smith.core.models.SecurityContext

### PodSecurityContext

::: k8smith.core.models.PodSecurityContext

## Networking

### ServicePort

::: k8smith.core.models.ServicePort

### ContainerPort

::: k8smith.core.models.ContainerPort

## Scheduling

### Toleration

::: k8smith.core.models.Toleration
