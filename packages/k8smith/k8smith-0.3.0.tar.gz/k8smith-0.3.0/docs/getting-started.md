# Getting Started

## Installation

=== "pip"

    ```bash
    pip install k8smith
    ```

=== "uv"

    ```bash
    uv add k8smith
    ```

=== "poetry"

    ```bash
    poetry add k8smith
    ```

## Basic Usage

### Creating a Deployment

```python
from k8smith import (
    DeploymentSpec,
    Container,
    PodSpec,
    PodTemplateSpec,
    build_deployment,
)

spec = DeploymentSpec(
    name="nginx",
    namespace="default",
    replicas=2,
    template=PodTemplateSpec(
        spec=PodSpec(
            containers=[
                Container(name="nginx", image="nginx:1.25")
            ]
        )
    ),
)

deployment = build_deployment(spec)
```

### Creating a Service

```python
from k8smith import ServiceSpec, ServicePort, build_service

spec = ServiceSpec(
    name="nginx",
    namespace="default",
    selector={"app": "nginx"},
    ports=[ServicePort(port=80, target_port=80)],
)

service = build_service(spec)
```

### Creating an Ingress

```python
from k8smith import IngressSpec, IngressRule, IngressTLS, build_ingress

spec = IngressSpec(
    name="web-ingress",
    namespace="default",
    rules=[
        IngressRule(
            host="example.com",
            http={
                "paths": [
                    {
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {"service": {"name": "nginx", "port": {"number": 80}}},
                    }
                ]
            },
        )
    ],
)

ingress = build_ingress(spec)
```

To target a specific ingress controller, use `ingress_class_name`:

```python
spec = IngressSpec(
    name="web-ingress",
    namespace="default",
    ingress_class_name="traefik",  # or: haproxy, contour, etc.
    rules=[...],
)
```

With TLS:

```python
spec = IngressSpec(
    name="secure-ingress",
    namespace="default",
    annotations={"cert-manager.io/cluster-issuer": "letsencrypt-prod"},
    tls=[IngressTLS(hosts=["example.com"], secret_name="example-tls")],
    rules=[
        IngressRule(
            host="example.com",
            http={
                "paths": [
                    {
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {"service": {"name": "nginx", "port": {"number": 80}}},
                    }
                ]
            },
        )
    ],
)
```

### Combining Resources with Manifest

```python
from k8smith import Manifest

manifest = Manifest()
manifest.add(deployment)
manifest.add(service)

# Output as YAML
print(manifest.to_yaml())

# Or write to file
manifest.to_file("manifests/nginx.yaml")
```

## Resource Requests and Limits

```python
from k8smith import Container, ResourceRequirements, ResourceQuantity

container = Container(
    name="app",
    image="myapp:v1",
    resources=ResourceRequirements(
        requests=ResourceQuantity(cpu="100m", memory="128Mi"),
        limits=ResourceQuantity(cpu="500m", memory="512Mi"),
    ),
)
```

### GPU Support

k8smith makes it easy to request GPU resources:

```python
from k8smith import ResourceQuantity

resources = ResourceRequirements(
    requests=ResourceQuantity(memory="4Gi"),
    limits=ResourceQuantity(
        memory="8Gi",
        extended={"nvidia.com/gpu": "1"},
    ),
)
```

## Available Resources

### Core Kubernetes

| Resource | Spec Class | Builder Function |
|----------|------------|------------------|
| Deployment | `DeploymentSpec` | `build_deployment()` |
| Service | `ServiceSpec` | `build_service()` |
| Ingress | `IngressSpec` | `build_ingress()` |
| StatefulSet | `StatefulSetSpec` | `build_statefulset()` |
| DaemonSet | `DaemonSetSpec` | `build_daemonset()` |
| CronJob | `CronJobSpec` | `build_cronjob()` |
| ConfigMap | `ConfigMapSpec` | `build_configmap()` |
| Secret | `SecretSpec` | `build_secret()` |
| HPA | `HPASpec` | `build_hpa()` |
| PDB | `PDBSpec` | `build_pdb()` |
| ServiceAccount | `ServiceAccountSpec` | `build_serviceaccount()` |
| Namespace | `NamespaceSpec` | `build_namespace()` |
| Role | `RoleSpec` | `build_role()` |
| ClusterRole | `ClusterRoleSpec` | `build_clusterrole()` |
| RoleBinding | `RoleBindingSpec` | `build_rolebinding()` |
| ClusterRoleBinding | `ClusterRoleBindingSpec` | `build_clusterrolebinding()` |

### GKE Extensions

| Resource | Spec Class | Builder Function |
|----------|------------|------------------|
| Gateway | `GatewaySpec` | `build_gateway()` |
| HTTPRoute | `HTTPRouteSpec` | `build_httproute()` |
| HealthCheckPolicy | `HealthCheckPolicySpec` | `build_healthcheckpolicy()` |
| GCPBackendPolicy | `GCPBackendPolicySpec` | `build_gcp_backend_policy()` |
| PodMonitoring | `PodMonitoringSpec` | `build_pod_monitoring()` |
| ClusterPodMonitoring | `ClusterPodMonitoringSpec` | `build_cluster_pod_monitoring()` |

## Next Steps

- [Production Web App Guide](guides/web-app.md) — Complete example
- [RBAC Guide](guides/rbac.md) — Setting up roles and permissions
- [GKE Guide](guides/gke.md) — GKE-specific resources
