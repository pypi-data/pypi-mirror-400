# GKE Resources

k8smith includes extensions for Google Kubernetes Engine (GKE) specific resources.

## Gateway API

### Gateway

Create a GKE Gateway for external load balancing:

```python
from k8smith.gke import GatewaySpec, build_gateway

gateway = build_gateway(
    GatewaySpec(
        name="main-gateway",
        namespace="gateway",
        gateway_class_name="gke-l7-global-external-managed",
        listeners=[
            {
                "name": "https",
                "port": 443,
                "protocol": "HTTPS",
                "tls": {
                    "mode": "Terminate",
                    "certificateRefs": [
                        {"name": "my-cert", "kind": "Secret"}
                    ],
                },
            },
            {
                "name": "http",
                "port": 80,
                "protocol": "HTTP",
            },
        ],
    )
)
```

### HTTPRoute

Route traffic to your services:

```python
from k8smith.gke import HTTPRouteSpec, build_httproute

route = build_httproute(
    HTTPRouteSpec(
        name="api-route",
        namespace="production",
        parent_refs=[
            {"name": "main-gateway", "namespace": "gateway"}
        ],
        hostnames=["api.example.com"],
        rules=[
            {
                "matches": [{"path": {"type": "PathPrefix", "value": "/v1"}}],
                "backendRefs": [
                    {"name": "api-v1", "port": 80}
                ],
            },
            {
                "matches": [{"path": {"type": "PathPrefix", "value": "/v2"}}],
                "backendRefs": [
                    {"name": "api-v2", "port": 80}
                ],
            },
        ],
    )
)
```

## Health Check Policy

Configure custom health checks for your backends:

```python
from k8smith.gke import HealthCheckPolicySpec, build_healthcheckpolicy

policy = build_healthcheckpolicy(
    HealthCheckPolicySpec(
        name="api-healthcheck",
        namespace="production",
        target_ref={
            "group": "",
            "kind": "Service",
            "name": "api-service",
        },
        config={
            "type": "HTTP",
            "httpHealthCheck": {
                "port": 8080,
                "requestPath": "/healthz",
            },
            "checkIntervalSec": 15,
            "timeoutSec": 5,
            "healthyThreshold": 2,
            "unhealthyThreshold": 3,
        },
    )
)
```

## GCP Backend Policy

Configure backend service settings like Cloud CDN and IAP:

```python
from k8smith.gke import GCPBackendPolicySpec, build_gcp_backend_policy

policy = build_gcp_backend_policy(
    GCPBackendPolicySpec(
        name="api-backend-policy",
        namespace="production",
        target_ref={
            "group": "",
            "kind": "Service",
            "name": "api-service",
        },
        default={
            "connectionDraining": {"drainingTimeoutSec": 30},
            "logging": {"enabled": True, "sampleRate": 1.0},
            "securityPolicy": "my-security-policy",
        },
    )
)
```

### With Cloud CDN

```python
policy = build_gcp_backend_policy(
    GCPBackendPolicySpec(
        name="static-backend-policy",
        namespace="production",
        target_ref={
            "group": "",
            "kind": "Service",
            "name": "static-assets",
        },
        default={
            "cdn": {
                "enabled": True,
                "cachePolicy": {
                    "includeHost": True,
                    "includeProtocol": True,
                    "includeQueryString": False,
                },
            },
        },
    )
)
```

## PodMonitoring

Set up Prometheus-style monitoring with Google Cloud Managed Prometheus:

```python
from k8smith.gke import PodMonitoringSpec, build_pod_monitoring

monitoring = build_pod_monitoring(
    PodMonitoringSpec(
        name="api-monitoring",
        namespace="production",
        selector={"app": "api-server"},
        endpoints=[
            {
                "port": "metrics",
                "interval": "30s",
                "path": "/metrics",
            }
        ],
    )
)
```

### ClusterPodMonitoring

For cluster-wide monitoring:

```python
from k8smith.gke import ClusterPodMonitoringSpec, build_cluster_pod_monitoring

monitoring = build_cluster_pod_monitoring(
    ClusterPodMonitoringSpec(
        name="all-apps-monitoring",
        selector={"monitored": "true"},
        endpoints=[
            {
                "port": "metrics",
                "interval": "30s",
            }
        ],
    )
)
```

## Complete Example

Here's a complete example setting up a GKE ingress stack:

```python
from k8smith import Manifest
from k8smith.gke import (
    GatewaySpec,
    HTTPRouteSpec,
    HealthCheckPolicySpec,
    GCPBackendPolicySpec,
    PodMonitoringSpec,
    build_gateway,
    build_httproute,
    build_healthcheckpolicy,
    build_gcp_backend_policy,
    build_pod_monitoring,
)

manifest = Manifest()

# Gateway
manifest.add(
    build_gateway(
        GatewaySpec(
            name="external-gateway",
            namespace="gateway",
            gateway_class_name="gke-l7-global-external-managed",
            listeners=[
                {"name": "https", "port": 443, "protocol": "HTTPS"},
            ],
        )
    )
)

# HTTPRoute
manifest.add(
    build_httproute(
        HTTPRouteSpec(
            name="app-routes",
            namespace="production",
            parent_refs=[{"name": "external-gateway", "namespace": "gateway"}],
            hostnames=["app.example.com"],
            rules=[
                {
                    "matches": [{"path": {"type": "PathPrefix", "value": "/"}}],
                    "backendRefs": [{"name": "app-service", "port": 80}],
                }
            ],
        )
    )
)

# Health Check
manifest.add(
    build_healthcheckpolicy(
        HealthCheckPolicySpec(
            name="app-healthcheck",
            namespace="production",
            target_ref={"group": "", "kind": "Service", "name": "app-service"},
            config={
                "type": "HTTP",
                "httpHealthCheck": {"port": 8080, "requestPath": "/healthz"},
            },
        )
    )
)

# Monitoring
manifest.add(
    build_pod_monitoring(
        PodMonitoringSpec(
            name="app-monitoring",
            namespace="production",
            selector={"app": "app-service"},
            endpoints=[{"port": "metrics", "interval": "30s"}],
        )
    )
)

print(manifest.to_yaml())
```
