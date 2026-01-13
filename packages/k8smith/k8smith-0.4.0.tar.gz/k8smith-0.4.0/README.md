# k8smith

[![CI](https://github.com/eliminyro/k8smith/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/eliminyro/k8smith/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/k8smith)](https://pypi.org/project/k8smith/)
[![Python 3.11+](https://img.shields.io/pypi/pyversions/k8smith)](https://pypi.org/project/k8smith/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

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

## Quick Start

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

# Collect resources into a manifest
manifest = Manifest()
manifest.add(deployment)
print(manifest.to_yaml())
```

## GPU Support (no workarounds needed!)

```python
from k8smith import (
    Container,
    ResourceRequirements,
    ResourceQuantity,
)

container = Container(
    name="ml-worker",
    image="ml-training:v1",
    resources=ResourceRequirements(
        requests=ResourceQuantity(memory="4Gi", cpu="1"),
        limits=ResourceQuantity(
            memory="8Gi",
            extended={"nvidia.com/gpu": "1"},  # Just works!
        ),
    ),
)
```

## GKE Extensions

```python
from k8smith.gke import (
    GatewaySpec,
    HTTPRouteSpec,
    build_gateway,
    build_httproute,
)

gateway = build_gateway(GatewaySpec(
    name="main-gateway",
    namespace="gateway",
    gateway_class_name="gke-l7-global-external-managed",
    listeners=[{
        "name": "https",
        "port": 443,
        "protocol": "HTTPS",
    }],
))
```

## Core Resources

| Resource | Builder |
|----------|---------|
| Deployment | `build_deployment(DeploymentSpec)` |
| Service | `build_service(ServiceSpec)` |
| Ingress | `build_ingress(IngressSpec)` |
| StatefulSet | `build_statefulset(StatefulSetSpec)` |
| DaemonSet | `build_daemonset(DaemonSetSpec)` |
| CronJob | `build_cronjob(CronJobSpec)` |
| ConfigMap | `build_configmap(ConfigMapSpec)` |
| Secret | `build_secret(SecretSpec)` |
| HPA | `build_hpa(HPASpec)` |
| PDB | `build_pdb(PDBSpec)` |
| ServiceAccount | `build_serviceaccount(ServiceAccountSpec)` |
| Namespace | `build_namespace(NamespaceSpec)` |
| Role | `build_role(RoleSpec)` |
| ClusterRole | `build_clusterrole(ClusterRoleSpec)` |
| RoleBinding | `build_rolebinding(RoleBindingSpec)` |
| ClusterRoleBinding | `build_clusterrolebinding(ClusterRoleBindingSpec)` |

## GKE Resources

| Resource | Builder |
|----------|---------|
| Gateway | `build_gateway(GatewaySpec)` |
| HTTPRoute | `build_httproute(HTTPRouteSpec)` |
| HealthCheckPolicy | `build_healthcheckpolicy(HealthCheckPolicySpec)` |
| GCPBackendPolicy | `build_gcp_backend_policy(GCPBackendPolicySpec)` |
| PodMonitoring | `build_pod_monitoring(PodMonitoringSpec)` |
| ClusterPodMonitoring | `build_cluster_pod_monitoring(ClusterPodMonitoringSpec)` |

## Why not cdk8s?

k8smith was created to replace cdk8s after encountering these issues:

| cdk8s Problem | k8smith Solution |
|---------------|-------------------|
| `Size.gibibytes(6)` outputs `6144Mi` | Strings stay as strings: `"6Gi"` |
| Can't add `nvidia.com/gpu` via resources | Built into `ResourceQuantity.extended` |
| Adds `hostNetwork: false` when not set | Only outputs what you specify |
| Requires label cleanup post-processing | No generated labels |
| JSII/Node.js dependency | Pure Python |

## License

GPL-3.0 - See [LICENSE](LICENSE) for details.
