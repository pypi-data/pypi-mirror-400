"""Pydantic models for Kubernetes resources.

These models provide type-safe input validation for Kubernetes resource specifications.
They use Pydantic's alias feature to support both Python snake_case and Kubernetes camelCase.

All models support `model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)`
for clean YAML output.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_serializer

# =============================================================================
# Base Model
# =============================================================================


class KubeModel(BaseModel):
    """Base model for all Kubernetes resources.

    Provides common configuration and serialization behavior.
    """

    model_config = ConfigDict(populate_by_name=True)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dict suitable for Kubernetes YAML.

        Excludes None values and empty collections.
        """
        return _clean_dict(self.model_dump(by_alias=True, exclude_none=True))


def _clean_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Remove empty lists and dicts recursively."""
    result: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, dict):
            cleaned = _clean_dict(v)
            if cleaned:  # Only include non-empty dicts
                result[k] = cleaned
        elif isinstance(v, list):
            if v:  # Only include non-empty lists
                cleaned_list: list[Any] = [
                    _clean_dict(item) if isinstance(item, dict) else item for item in v
                ]
                result[k] = cleaned_list
        else:
            result[k] = v
    return result


# =============================================================================
# Base Primitives
# =============================================================================


class ResourceQuantity(KubeModel):
    """Kubernetes resource quantity (e.g., '100m', '512Mi', '2Gi').

    Example:
        >>> ResourceQuantity(cpu="100m", memory="512Mi")
        >>> ResourceQuantity(memory="4Gi", extended={"nvidia.com/gpu": "1"})
    """

    cpu: str | None = None
    memory: str | None = None
    extended: dict[str, str] = Field(default_factory=dict)

    @model_serializer
    def serialize(self) -> dict[str, str]:
        """Flatten extended resources into the main dict."""
        result: dict[str, str] = {}
        if self.cpu:
            result["cpu"] = self.cpu
        if self.memory:
            result["memory"] = self.memory
        # Flatten extended resources (e.g., nvidia.com/gpu)
        result.update(self.extended)
        return result


class ResourceRequirements(KubeModel):
    """Container resource requests and limits.

    Example:
        >>> ResourceRequirements(
        ...     requests=ResourceQuantity(cpu="100m", memory="128Mi"),
        ...     limits=ResourceQuantity(memory="256Mi"),
        ... )
    """

    requests: ResourceQuantity | None = None
    limits: ResourceQuantity | None = None


class ContainerPort(KubeModel):
    """Container port configuration.

    Example:
        >>> ContainerPort(container_port=8080, name="http")
        >>> ContainerPort(container_port=80, host_port=8080)
    """

    container_port: int = Field(alias="containerPort")
    host_port: int | None = Field(default=None, alias="hostPort")
    host_ip: str | None = Field(default=None, alias="hostIP")
    name: str | None = None
    protocol: Literal["TCP", "UDP", "SCTP"] = "TCP"


class EnvVar(KubeModel):
    """Environment variable.

    Example:
        >>> EnvVar(name="DATABASE_URL", value="postgres://localhost/db")
        >>> EnvVar(name="POD_NAME", value_from={"fieldRef": {"fieldPath": "metadata.name"}})
    """

    name: str
    value: str | None = None
    value_from: dict | None = Field(default=None, alias="valueFrom")


class EnvFromSource(KubeModel):
    """Environment from ConfigMap or Secret.

    Example:
        >>> EnvFromSource(config_map_ref={"name": "my-config"})
        >>> EnvFromSource(secret_ref={"name": "my-secret"})
    """

    config_map_ref: dict | None = Field(default=None, alias="configMapRef")
    secret_ref: dict | None = Field(default=None, alias="secretRef")
    prefix: str | None = None


class Probe(KubeModel):
    """Liveness/Readiness/Startup probe configuration.

    Example:
        >>> Probe(
        ...     http_get={"path": "/health", "port": 8080},
        ...     initial_delay_seconds=30,
        ...     period_seconds=10,
        ... )
    """

    http_get: dict | None = Field(default=None, alias="httpGet")
    tcp_socket: dict | None = Field(default=None, alias="tcpSocket")
    exec_: dict | None = Field(default=None, alias="exec")
    grpc: dict | None = None
    initial_delay_seconds: int | None = Field(default=None, alias="initialDelaySeconds")
    period_seconds: int | None = Field(default=None, alias="periodSeconds")
    timeout_seconds: int | None = Field(default=None, alias="timeoutSeconds")
    success_threshold: int | None = Field(default=None, alias="successThreshold")
    failure_threshold: int | None = Field(default=None, alias="failureThreshold")


class VolumeMount(KubeModel):
    """Container volume mount.

    Example:
        >>> VolumeMount(name="config", mount_path="/etc/config", read_only=True)
    """

    name: str
    mount_path: str = Field(alias="mountPath")
    read_only: bool | None = Field(default=None, alias="readOnly")
    sub_path: str | None = Field(default=None, alias="subPath")
    sub_path_expr: str | None = Field(default=None, alias="subPathExpr")


class Volume(KubeModel):
    """Pod volume definition.

    Example:
        >>> Volume(name="config", config_map={"name": "my-config"})
        >>> Volume(name="data", empty_dir={})
        >>> Volume(name="secrets", csi={"driver": "secrets-store.csi.k8s.io", "readOnly": True})
    """

    name: str
    config_map: dict | None = Field(default=None, alias="configMap")
    secret: dict | None = None
    empty_dir: dict | None = Field(default=None, alias="emptyDir")
    persistent_volume_claim: dict | None = Field(default=None, alias="persistentVolumeClaim")
    host_path: dict | None = Field(default=None, alias="hostPath")
    projected: dict | None = None
    downward_api: dict | None = Field(default=None, alias="downwardAPI")
    csi: dict | None = None


class SecurityContext(KubeModel):
    """Container security context.

    Example:
        >>> SecurityContext(
        ...     run_as_non_root=True,
        ...     read_only_root_filesystem=True,
        ...     allow_privilege_escalation=False,
        ... )
    """

    run_as_user: int | None = Field(default=None, alias="runAsUser")
    run_as_group: int | None = Field(default=None, alias="runAsGroup")
    run_as_non_root: bool | None = Field(default=None, alias="runAsNonRoot")
    read_only_root_filesystem: bool | None = Field(default=None, alias="readOnlyRootFilesystem")
    privileged: bool | None = None
    allow_privilege_escalation: bool | None = Field(default=None, alias="allowPrivilegeEscalation")
    capabilities: dict | None = None
    seccomp_profile: dict | None = Field(default=None, alias="seccompProfile")


class Toleration(KubeModel):
    """Pod toleration.

    Example:
        >>> Toleration(key="nvidia.com/gpu", operator="Exists", effect="NoSchedule")
    """

    key: str | None = None
    operator: Literal["Exists", "Equal"] | None = None
    value: str | None = None
    effect: Literal["NoSchedule", "PreferNoSchedule", "NoExecute"] | None = None
    toleration_seconds: int | None = Field(default=None, alias="tolerationSeconds")


# =============================================================================
# Container
# =============================================================================


class Container(KubeModel):
    """Container specification.

    Example:
        >>> Container(
        ...     name="web",
        ...     image="nginx:1.25",
        ...     ports=[ContainerPort(container_port=80)],
        ...     resources=ResourceRequirements(
        ...         requests=ResourceQuantity(cpu="100m", memory="128Mi"),
        ...     ),
        ... )
    """

    name: str
    image: str
    image_pull_policy: Literal["Always", "IfNotPresent", "Never"] | None = Field(
        default=None, alias="imagePullPolicy"
    )
    command: list[str] | None = None
    args: list[str] | None = None
    working_dir: str | None = Field(default=None, alias="workingDir")
    env: list[EnvVar] | None = None
    env_from: list[EnvFromSource] | None = Field(default=None, alias="envFrom")
    ports: list[ContainerPort] | None = None
    resources: ResourceRequirements | None = None
    volume_mounts: list[VolumeMount] | None = Field(default=None, alias="volumeMounts")
    liveness_probe: Probe | None = Field(default=None, alias="livenessProbe")
    readiness_probe: Probe | None = Field(default=None, alias="readinessProbe")
    startup_probe: Probe | None = Field(default=None, alias="startupProbe")
    security_context: SecurityContext | None = Field(default=None, alias="securityContext")
    stdin: bool | None = None
    tty: bool | None = None


# =============================================================================
# Pod Template
# =============================================================================


class PodSecurityContext(KubeModel):
    """Pod-level security context.

    Example:
        >>> PodSecurityContext(run_as_non_root=True, fs_group=1000)
    """

    run_as_user: int | None = Field(default=None, alias="runAsUser")
    run_as_group: int | None = Field(default=None, alias="runAsGroup")
    run_as_non_root: bool | None = Field(default=None, alias="runAsNonRoot")
    fs_group: int | None = Field(default=None, alias="fsGroup")
    fs_group_change_policy: str | None = Field(default=None, alias="fsGroupChangePolicy")
    supplemental_groups: list[int] | None = Field(default=None, alias="supplementalGroups")
    seccomp_profile: dict | None = Field(default=None, alias="seccompProfile")


class PodSpec(KubeModel):
    """Pod specification.

    Example:
        >>> PodSpec(
        ...     containers=[Container(name="app", image="myapp:v1")],
        ...     service_account_name="my-sa",
        ... )
    """

    containers: list[Container]
    init_containers: list[Container] | None = Field(default=None, alias="initContainers")
    volumes: list[Volume] | None = None
    service_account_name: str | None = Field(default=None, alias="serviceAccountName")
    automount_service_account_token: bool | None = Field(
        default=None, alias="automountServiceAccountToken"
    )
    node_selector: dict[str, str] | None = Field(default=None, alias="nodeSelector")
    node_name: str | None = Field(default=None, alias="nodeName")
    tolerations: list[Toleration] | None = None
    affinity: dict | None = None
    host_network: bool | None = Field(default=None, alias="hostNetwork")
    host_pid: bool | None = Field(default=None, alias="hostPID")
    dns_policy: str | None = Field(default=None, alias="dnsPolicy")
    dns_config: dict | None = Field(default=None, alias="dnsConfig")
    security_context: PodSecurityContext | None = Field(default=None, alias="securityContext")
    image_pull_secrets: list[dict] | None = Field(default=None, alias="imagePullSecrets")
    restart_policy: Literal["Always", "OnFailure", "Never"] | None = Field(
        default=None, alias="restartPolicy"
    )
    termination_grace_period_seconds: int | None = Field(
        default=None, alias="terminationGracePeriodSeconds"
    )
    priority_class_name: str | None = Field(default=None, alias="priorityClassName")


class PodTemplateSpec(KubeModel):
    """Pod template for Deployment, StatefulSet, etc.

    Example:
        >>> PodTemplateSpec(
        ...     metadata={"labels": {"app": "web"}},
        ...     spec=PodSpec(containers=[Container(name="web", image="nginx")]),
        ... )
    """

    metadata: dict | None = None
    spec: PodSpec


# =============================================================================
# Workload Specifications
# =============================================================================


class DeploymentSpec(KubeModel):
    """Deployment specification.

    Example:
        >>> DeploymentSpec(
        ...     name="web",
        ...     namespace="production",
        ...     replicas=3,
        ...     template=PodTemplateSpec(...),
        ... )
    """

    name: str
    namespace: str
    replicas: int | None = None
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    selector: dict[str, str] | None = None
    template: PodTemplateSpec
    strategy: dict | None = None
    min_ready_seconds: int | None = Field(default=None, alias="minReadySeconds")
    revision_history_limit: int | None = Field(default=None, alias="revisionHistoryLimit")
    progress_deadline_seconds: int | None = Field(default=None, alias="progressDeadlineSeconds")
    paused: bool | None = None


class StatefulSetSpec(KubeModel):
    """StatefulSet specification.

    Example:
        >>> StatefulSetSpec(
        ...     name="db",
        ...     namespace="production",
        ...     service_name="db-headless",
        ...     template=PodTemplateSpec(...),
        ... )
    """

    name: str
    namespace: str
    replicas: int | None = None
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    selector: dict[str, str] | None = None
    template: PodTemplateSpec
    service_name: str = Field(alias="serviceName")
    volume_claim_templates: list[dict] | None = Field(default=None, alias="volumeClaimTemplates")
    pod_management_policy: Literal["OrderedReady", "Parallel"] | None = Field(
        default=None, alias="podManagementPolicy"
    )
    update_strategy: dict | None = Field(default=None, alias="updateStrategy")
    revision_history_limit: int | None = Field(default=None, alias="revisionHistoryLimit")
    min_ready_seconds: int | None = Field(default=None, alias="minReadySeconds")
    persistent_volume_claim_retention_policy: dict | None = Field(
        default=None, alias="persistentVolumeClaimRetentionPolicy"
    )


class DaemonSetSpec(KubeModel):
    """DaemonSet specification.

    Example:
        >>> DaemonSetSpec(
        ...     name="node-agent",
        ...     namespace="kube-system",
        ...     template=PodTemplateSpec(...),
        ... )
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    selector: dict[str, str] | None = None
    template: PodTemplateSpec
    update_strategy: dict | None = Field(default=None, alias="updateStrategy")
    min_ready_seconds: int | None = Field(default=None, alias="minReadySeconds")
    revision_history_limit: int | None = Field(default=None, alias="revisionHistoryLimit")


class CronJobSpec(KubeModel):
    """CronJob specification.

    Example:
        >>> CronJobSpec(
        ...     name="backup",
        ...     namespace="production",
        ...     schedule="0 2 * * *",
        ...     job_template=PodTemplateSpec(...),
        ... )
    """

    name: str
    namespace: str
    schedule: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    job_template: PodTemplateSpec = Field(alias="jobTemplate")
    concurrency_policy: Literal["Allow", "Forbid", "Replace"] | None = Field(
        default=None, alias="concurrencyPolicy"
    )
    successful_jobs_history_limit: int | None = Field(
        default=None, alias="successfulJobsHistoryLimit"
    )
    failed_jobs_history_limit: int | None = Field(default=None, alias="failedJobsHistoryLimit")
    starting_deadline_seconds: int | None = Field(default=None, alias="startingDeadlineSeconds")
    suspend: bool | None = None
    time_zone: str | None = Field(default=None, alias="timeZone")


# =============================================================================
# Service
# =============================================================================


class ServicePort(KubeModel):
    """Service port configuration.

    Example:
        >>> ServicePort(port=80, target_port=8080, name="http")
    """

    port: int
    target_port: int | str | None = Field(default=None, alias="targetPort")
    name: str | None = None
    protocol: Literal["TCP", "UDP", "SCTP"] | None = None
    node_port: int | None = Field(default=None, alias="nodePort")
    app_protocol: str | None = Field(default=None, alias="appProtocol")


class ServiceSpec(KubeModel):
    """Service specification.

    Example:
        >>> ServiceSpec(
        ...     name="web",
        ...     namespace="production",
        ...     ports=[ServicePort(port=80, target_port=8080)],
        ...     selector={"app": "web"},
        ... )
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    selector: dict[str, str] | None = None
    ports: list[ServicePort] | None = None
    type: Literal["ClusterIP", "NodePort", "LoadBalancer", "ExternalName"] | None = None
    cluster_ip: str | None = Field(default=None, alias="clusterIP")
    external_name: str | None = Field(default=None, alias="externalName")
    external_traffic_policy: Literal["Cluster", "Local"] | None = Field(
        default=None, alias="externalTrafficPolicy"
    )
    internal_traffic_policy: Literal["Cluster", "Local"] | None = Field(
        default=None, alias="internalTrafficPolicy"
    )
    session_affinity: Literal["ClientIP", "None"] | None = Field(
        default=None, alias="sessionAffinity"
    )
    load_balancer_ip: str | None = Field(default=None, alias="loadBalancerIP")
    load_balancer_source_ranges: list[str] | None = Field(
        default=None, alias="loadBalancerSourceRanges"
    )


# =============================================================================
# Other Resources
# =============================================================================


class ConfigMapSpec(KubeModel):
    """ConfigMap specification.

    Example:
        >>> ConfigMapSpec(
        ...     name="app-config",
        ...     namespace="production",
        ...     data={"config.yaml": "key: value"},
        ... )
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    data: dict[str, str] | None = None
    binary_data: dict[str, str] | None = Field(default=None, alias="binaryData")
    immutable: bool | None = None


class SecretSpec(KubeModel):
    """Secret specification.

    Example:
        >>> SecretSpec(
        ...     name="db-credentials",
        ...     namespace="production",
        ...     string_data={"username": "admin", "password": "secret"},
        ... )
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    data: dict[str, str] | None = None
    string_data: dict[str, str] | None = Field(default=None, alias="stringData")
    type: str | None = None
    immutable: bool | None = None


class HPASpec(KubeModel):
    """HorizontalPodAutoscaler specification.

    Example:
        >>> HPASpec(
        ...     name="web-hpa",
        ...     namespace="production",
        ...     scale_target_ref={"apiVersion": "apps/v1", "kind": "Deployment", "name": "web"},
        ...     min_replicas=2,
        ...     max_replicas=10,
        ... )
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    scale_target_ref: dict = Field(alias="scaleTargetRef")
    min_replicas: int | None = Field(default=None, alias="minReplicas")
    max_replicas: int = Field(alias="maxReplicas")
    metrics: list[dict] | None = None
    behavior: dict | None = None


class PDBSpec(KubeModel):
    """PodDisruptionBudget specification.

    Example:
        >>> PDBSpec(
        ...     name="web-pdb",
        ...     namespace="production",
        ...     selector={"app": "web"},
        ...     min_available=1,
        ... )
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    selector: dict[str, str] | None = None
    min_available: int | str | None = Field(default=None, alias="minAvailable")
    max_unavailable: int | str | None = Field(default=None, alias="maxUnavailable")


class ServiceAccountSpec(KubeModel):
    """ServiceAccount specification.

    Example:
        >>> ServiceAccountSpec(name="app-sa", namespace="production")
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    automount_service_account_token: bool | None = Field(
        default=None, alias="automountServiceAccountToken"
    )
    image_pull_secrets: list[dict] | None = Field(default=None, alias="imagePullSecrets")


class NamespaceSpec(KubeModel):
    """Namespace specification.

    Example:
        >>> NamespaceSpec(name="production", labels={"env": "prod"})
    """

    name: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None


# =============================================================================
# RBAC Resources
# =============================================================================


class PolicyRule(KubeModel):
    """RBAC policy rule for Role and ClusterRole.

    Example:
        >>> PolicyRule(
        ...     api_groups=[""],
        ...     resources=["pods", "pods/log"],
        ...     verbs=["get", "list", "watch"],
        ... )
        >>> PolicyRule(
        ...     api_groups=["apps"],
        ...     resources=["deployments"],
        ...     verbs=["get", "list", "watch", "create", "update", "patch", "delete"],
        ...     resource_names=["my-deployment"],
        ... )
    """

    api_groups: list[str] | None = Field(default=None, alias="apiGroups")
    resources: list[str] | None = None
    resource_names: list[str] | None = Field(default=None, alias="resourceNames")
    verbs: list[str]
    non_resource_urls: list[str] | None = Field(default=None, alias="nonResourceURLs")


class RoleSpec(KubeModel):
    """Role specification (namespaced RBAC).

    Example:
        >>> RoleSpec(
        ...     name="pod-reader",
        ...     namespace="production",
        ...     rules=[
        ...         PolicyRule(api_groups=[""], resources=["pods"], verbs=["get", "list", "watch"]),
        ...     ],
        ... )
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    rules: list[PolicyRule] | None = None


class ClusterRoleSpec(KubeModel):
    """ClusterRole specification (cluster-wide RBAC).

    Example:
        >>> ClusterRoleSpec(
        ...     name="node-reader",
        ...     rules=[
        ...         PolicyRule(
        ...             api_groups=[""],
        ...             resources=["nodes"],
        ...             verbs=["get", "list", "watch"],
        ...         ),
        ...     ],
        ... )
    """

    name: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    rules: list[PolicyRule] | None = None
    aggregation_rule: dict | None = Field(default=None, alias="aggregationRule")


class RoleBindingSubject(KubeModel):
    """Subject for RoleBinding and ClusterRoleBinding.

    Example:
        >>> RoleBindingSubject(kind="ServiceAccount", name="my-sa", namespace="production")
        >>> RoleBindingSubject(kind="User", name="jane@example.com")
        >>> RoleBindingSubject(kind="Group", name="developers")
    """

    kind: Literal["User", "Group", "ServiceAccount"]
    name: str
    namespace: str | None = None
    api_group: str | None = Field(default=None, alias="apiGroup")


class RoleRef(KubeModel):
    """Reference to a Role or ClusterRole.

    Example:
        >>> RoleRef(kind="Role", name="pod-reader", api_group="rbac.authorization.k8s.io")
        >>> RoleRef(kind="ClusterRole", name="admin", api_group="rbac.authorization.k8s.io")
    """

    kind: Literal["Role", "ClusterRole"]
    name: str
    api_group: str = Field(default="rbac.authorization.k8s.io", alias="apiGroup")


class RoleBindingSpec(KubeModel):
    """RoleBinding specification (namespaced binding).

    Example:
        >>> RoleBindingSpec(
        ...     name="read-pods",
        ...     namespace="production",
        ...     subjects=[
        ...         RoleBindingSubject(kind="ServiceAccount", name="my-sa", namespace="production"),
        ...     ],
        ...     role_ref=RoleRef(kind="Role", name="pod-reader"),
        ... )
    """

    name: str
    namespace: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    subjects: list[RoleBindingSubject] | None = None
    role_ref: RoleRef = Field(alias="roleRef")


class ClusterRoleBindingSpec(KubeModel):
    """ClusterRoleBinding specification (cluster-wide binding).

    Example:
        >>> ClusterRoleBindingSpec(
        ...     name="read-nodes",
        ...     subjects=[
        ...         RoleBindingSubject(
        ...             kind="ServiceAccount",
        ...             name="monitoring",
        ...             namespace="kube-system",
        ...         ),
        ...     ],
        ...     role_ref=RoleRef(kind="ClusterRole", name="node-reader"),
        ... )
    """

    name: str
    labels: dict[str, str] | None = None
    annotations: dict[str, str] | None = None
    subjects: list[RoleBindingSubject] | None = None
    role_ref: RoleRef = Field(alias="roleRef")
