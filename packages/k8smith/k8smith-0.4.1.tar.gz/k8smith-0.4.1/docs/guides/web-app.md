# Production Web App

This guide demonstrates generating a complete set of Kubernetes resources for a production web application with:

- ServiceAccount
- ConfigMap (application configuration)
- Secret (database credentials)
- Deployment (with probes, resources, security context, affinity)
- Service
- HorizontalPodAutoscaler
- PodDisruptionBudget

## Setup

First, define your application configuration:

```python
from k8smith import (
    Container,
    ContainerPort,
    DeploymentSpec,
    EnvVar,
    Manifest,
    PodSpec,
    PodTemplateSpec,
    Probe,
    ResourceQuantity,
    ResourceRequirements,
    ServicePort,
    ServiceSpec,
    Toleration,
    Volume,
    VolumeMount,
    build_configmap,
    build_deployment,
    build_hpa,
    build_pdb,
    build_secret,
    build_service,
    build_serviceaccount,
)
from k8smith.core.models import (
    ConfigMapSpec,
    HPASpec,
    PDBSpec,
    PodSecurityContext,
    SecretSpec,
    SecurityContext,
    ServiceAccountSpec,
)

APP_NAME = "api-server"
NAMESPACE = "production"
IMAGE = "mycompany/api-server:v1.2.3"
REPLICAS = 3

COMMON_LABELS = {
    "app.kubernetes.io/name": APP_NAME,
    "app.kubernetes.io/component": "backend",
    "app.kubernetes.io/part-of": "myapp",
    "app.kubernetes.io/managed-by": "k8smith",
}

SELECTOR = {"app.kubernetes.io/name": APP_NAME}
```

## ServiceAccount

Create a ServiceAccount for the application:

```python
def create_service_account() -> dict:
    return build_serviceaccount(
        ServiceAccountSpec(
            name=APP_NAME,
            namespace=NAMESPACE,
            labels=COMMON_LABELS,
        )
    )
```

## ConfigMap

Store application configuration in a ConfigMap:

```python
def create_configmap() -> dict:
    return build_configmap(
        ConfigMapSpec(
            name=f"{APP_NAME}-config",
            namespace=NAMESPACE,
            labels=COMMON_LABELS,
            data={
                "config.yaml": """\
server:
  port: 8080
  read_timeout: 30s
  write_timeout: 30s

logging:
  level: info
  format: json

features:
  rate_limiting: true
  caching: true
""",
                "LOG_LEVEL": "info",
                "CACHE_TTL": "300",
            },
        )
    )
```

## Secret

Store sensitive data in a Secret:

```python
def create_secret() -> dict:
    return build_secret(
        SecretSpec(
            name=f"{APP_NAME}-secrets",
            namespace=NAMESPACE,
            labels=COMMON_LABELS,
            type="Opaque",
            string_data={
                "DATABASE_URL": "postgres://user:password@db.example.com:5432/myapp",
                "API_KEY": "super-secret-api-key",
            },
        )
    )
```

!!! warning
    In production, use external secret management (e.g., GCP Secret Manager, HashiCorp Vault) instead of storing secrets in manifests.

## Deployment

Create a production-ready Deployment with all best practices:

```python
def create_deployment() -> dict:
    return build_deployment(
        DeploymentSpec(
            name=APP_NAME,
            namespace=NAMESPACE,
            replicas=REPLICAS,
            labels=COMMON_LABELS,
            selector=SELECTOR,
            strategy={
                "type": "RollingUpdate",
                "rollingUpdate": {
                    "maxSurge": "25%",
                    "maxUnavailable": 0,
                },
            },
            template=PodTemplateSpec(
                metadata={
                    "labels": COMMON_LABELS,
                    "annotations": {
                        "prometheus.io/scrape": "true",
                        "prometheus.io/port": "8080",
                        "prometheus.io/path": "/metrics",
                    },
                },
                spec=PodSpec(
                    service_account_name=APP_NAME,
                    security_context=PodSecurityContext(
                        run_as_non_root=True,
                        run_as_user=1000,
                        run_as_group=1000,
                        fs_group=1000,
                    ),
                    containers=[
                        Container(
                            name=APP_NAME,
                            image=IMAGE,
                            image_pull_policy="IfNotPresent",
                            ports=[
                                ContainerPort(container_port=8080, name="http"),
                            ],
                            env=[
                                # From ConfigMap
                                EnvVar(
                                    name="LOG_LEVEL",
                                    value_from={
                                        "configMapKeyRef": {
                                            "name": f"{APP_NAME}-config",
                                            "key": "LOG_LEVEL",
                                        }
                                    },
                                ),
                                # From Secret
                                EnvVar(
                                    name="DATABASE_URL",
                                    value_from={
                                        "secretKeyRef": {
                                            "name": f"{APP_NAME}-secrets",
                                            "key": "DATABASE_URL",
                                        }
                                    },
                                ),
                                # Downward API
                                EnvVar(
                                    name="POD_NAME",
                                    value_from={"fieldRef": {"fieldPath": "metadata.name"}},
                                ),
                            ],
                            resources=ResourceRequirements(
                                requests=ResourceQuantity(cpu="100m", memory="256Mi"),
                                limits=ResourceQuantity(memory="512Mi"),
                            ),
                            volume_mounts=[
                                VolumeMount(
                                    name="config",
                                    mount_path="/etc/app",
                                    read_only=True,
                                ),
                            ],
                            liveness_probe=Probe(
                                http_get={"path": "/healthz", "port": 8080},
                                initial_delay_seconds=15,
                                period_seconds=20,
                                timeout_seconds=5,
                                failure_threshold=3,
                            ),
                            readiness_probe=Probe(
                                http_get={"path": "/ready", "port": 8080},
                                initial_delay_seconds=5,
                                period_seconds=10,
                                timeout_seconds=3,
                                failure_threshold=3,
                            ),
                            security_context=SecurityContext(
                                allow_privilege_escalation=False,
                                read_only_root_filesystem=True,
                                capabilities={"drop": ["ALL"]},
                            ),
                        ),
                    ],
                    volumes=[
                        Volume(
                            name="config",
                            config_map={"name": f"{APP_NAME}-config"},
                        ),
                    ],
                    tolerations=[
                        Toleration(
                            key="dedicated",
                            operator="Equal",
                            value="web",
                            effect="NoSchedule",
                        ),
                    ],
                    affinity={
                        "podAntiAffinity": {
                            "preferredDuringSchedulingIgnoredDuringExecution": [
                                {
                                    "weight": 100,
                                    "podAffinityTerm": {
                                        "labelSelector": {"matchLabels": SELECTOR},
                                        "topologyKey": "kubernetes.io/hostname",
                                    },
                                }
                            ]
                        }
                    },
                ),
            ),
        )
    )
```

## Service

Expose the application with a ClusterIP Service:

```python
def create_service() -> dict:
    return build_service(
        ServiceSpec(
            name=APP_NAME,
            namespace=NAMESPACE,
            labels=COMMON_LABELS,
            selector=SELECTOR,
            ports=[
                ServicePort(port=80, target_port=8080, name="http"),
            ],
            type="ClusterIP",
        )
    )
```

## HorizontalPodAutoscaler

Configure auto-scaling based on CPU and memory:

```python
def create_hpa() -> dict:
    return build_hpa(
        HPASpec(
            name=APP_NAME,
            namespace=NAMESPACE,
            labels=COMMON_LABELS,
            scale_target_ref={
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "name": APP_NAME,
            },
            min_replicas=REPLICAS,
            max_replicas=10,
            metrics=[
                {
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {"type": "Utilization", "averageUtilization": 70},
                    },
                },
                {
                    "type": "Resource",
                    "resource": {
                        "name": "memory",
                        "target": {"type": "Utilization", "averageUtilization": 80},
                    },
                },
            ],
            behavior={
                "scaleDown": {
                    "stabilizationWindowSeconds": 300,
                    "policies": [{"type": "Percent", "value": 10, "periodSeconds": 60}],
                },
                "scaleUp": {
                    "stabilizationWindowSeconds": 0,
                    "policies": [
                        {"type": "Percent", "value": 100, "periodSeconds": 15},
                        {"type": "Pods", "value": 4, "periodSeconds": 15},
                    ],
                    "selectPolicy": "Max",
                },
            },
        )
    )
```

## PodDisruptionBudget

Ensure high availability during node maintenance:

```python
def create_pdb() -> dict:
    return build_pdb(
        PDBSpec(
            name=APP_NAME,
            namespace=NAMESPACE,
            labels=COMMON_LABELS,
            selector=SELECTOR,
            min_available=2,
        )
    )
```

## Putting It All Together

```python
def main():
    manifest = Manifest()

    # Add resources in dependency order
    manifest.add(create_service_account())
    manifest.add(create_configmap())
    manifest.add(create_secret())
    manifest.add(create_deployment())
    manifest.add(create_service())
    manifest.add(create_hpa())
    manifest.add(create_pdb())

    # Output YAML
    print(manifest.to_yaml())

if __name__ == "__main__":
    main()
```

Run with:

```bash
python generate.py > manifests/web-app.yaml
kubectl apply -f manifests/web-app.yaml
```
