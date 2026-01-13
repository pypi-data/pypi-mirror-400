"""Pydantic models for GKE-specific resources."""

from pydantic import BaseModel, ConfigDict, Field


class GatewaySpec(BaseModel):
    """GKE Gateway specification.

    Example:
        >>> GatewaySpec(
        ...     name="main-gateway",
        ...     namespace="gateway",
        ...     gateway_class_name="gke-l7-global-external-managed",
        ...     listeners=[{"name": "https", "port": 443, "protocol": "HTTPS"}],
        ... )
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    namespace: str
    gateway_class_name: str = Field(alias="gatewayClassName")
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    listeners: list[dict] = Field(default_factory=list)
    addresses: list[dict] = Field(default_factory=list)


class HTTPRouteSpec(BaseModel):
    """GKE HTTPRoute specification.

    Example:
        >>> HTTPRouteSpec(
        ...     name="app-route",
        ...     namespace="production",
        ...     parent_refs=[{"name": "main-gateway", "namespace": "gateway"}],
        ...     hostnames=["app.example.com"],
        ...     rules=[{"matches": [{"path": {"value": "/"}}], "backendRefs": [...]}],
        ... )
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    namespace: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    parent_refs: list[dict] = Field(alias="parentRefs")
    hostnames: list[str] = Field(default_factory=list)
    rules: list[dict] = Field(default_factory=list)


class HealthCheckPolicySpec(BaseModel):
    """GKE HealthCheckPolicy specification.

    Example:
        >>> HealthCheckPolicySpec(
        ...     name="app-healthcheck",
        ...     namespace="production",
        ...     target_ref={"group": "", "kind": "Service", "name": "app"},
        ...     config={"type": "HTTP", "httpHealthCheck": {"requestPath": "/health"}},
        ... )
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    namespace: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    target_ref: dict = Field(alias="targetRef")
    config: dict = Field(default_factory=dict)


class GCPBackendPolicySpec(BaseModel):
    """GKE GCPBackendPolicy specification.

    Example:
        >>> GCPBackendPolicySpec(
        ...     name="app-backend-policy",
        ...     namespace="production",
        ...     target_ref={"group": "", "kind": "Service", "name": "app"},
        ...     config={"timeoutSec": 30, "connectionDraining": {"drainingTimeoutSec": 60}},
        ... )
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    namespace: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    target_ref: dict = Field(alias="targetRef")
    config: dict = Field(default_factory=dict)


class PodMonitoringSpec(BaseModel):
    """GKE PodMonitoring specification (Cloud Monitoring).

    Example:
        >>> PodMonitoringSpec(
        ...     name="app-monitoring",
        ...     namespace="production",
        ...     selector={"matchLabels": {"app": "web"}},
        ...     endpoints=[{"port": "metrics", "interval": "30s"}],
        ... )
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    namespace: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    selector: dict = Field(default_factory=dict)
    endpoints: list[dict] = Field(default_factory=list)
    target_labels: dict | None = Field(default=None, alias="targetLabels")


class ClusterPodMonitoringSpec(BaseModel):
    """GKE ClusterPodMonitoring specification.

    Example:
        >>> ClusterPodMonitoringSpec(
        ...     name="cluster-monitoring",
        ...     selector={"matchLabels": {"monitoring": "enabled"}},
        ...     endpoints=[{"port": "metrics", "interval": "60s"}],
        ... )
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    selector: dict = Field(default_factory=dict)
    endpoints: list[dict] = Field(default_factory=list)
    target_labels: dict | None = Field(default=None, alias="targetLabels")
