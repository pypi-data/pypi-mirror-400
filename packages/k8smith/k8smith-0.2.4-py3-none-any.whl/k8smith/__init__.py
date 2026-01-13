"""K8smith - A transparent, lightweight Kubernetes manifest generator."""

from importlib.metadata import version

__version__ = version("k8smith")

# GKE extension namespace
from k8smith import gke
from k8smith.core.configmap import build_configmap
from k8smith.core.cronjob import build_cronjob
from k8smith.core.daemonset import build_daemonset

# Core builders
from k8smith.core.deployment import build_deployment
from k8smith.core.hpa import build_hpa

# Core models
from k8smith.core.models import (
    ClusterRoleBindingSpec,
    ClusterRoleSpec,
    Container,
    ContainerPort,
    CronJobSpec,
    DaemonSetSpec,
    DeploymentSpec,
    EnvFromSource,
    EnvVar,
    PodSpec,
    PodTemplateSpec,
    PolicyRule,
    Probe,
    ResourceQuantity,
    ResourceRequirements,
    RoleBindingSpec,
    RoleBindingSubject,
    RoleRef,
    RoleSpec,
    SecurityContext,
    ServicePort,
    ServiceSpec,
    StatefulSetSpec,
    Toleration,
    Volume,
    VolumeMount,
)
from k8smith.core.namespace import build_namespace
from k8smith.core.pdb import build_pdb

# RBAC builders
from k8smith.core.rbac import (
    build_clusterrole,
    build_clusterrolebinding,
    build_role,
    build_rolebinding,
)
from k8smith.core.secret import build_secret
from k8smith.core.service import build_service
from k8smith.core.serviceaccount import build_serviceaccount
from k8smith.core.statefulset import build_statefulset

# Output utilities
from k8smith.output.manifest import Manifest
from k8smith.output.yaml import dump, dump_one, load

# Validation
from k8smith.validation import (
    ValidationError,
    ValidationMode,
    ValidationResult,
    validate_manifest,
)

__all__ = [
    "__version__",
    # RBAC Models
    "ClusterRoleBindingSpec",
    "ClusterRoleSpec",
    "PolicyRule",
    "RoleBindingSpec",
    "RoleBindingSubject",
    "RoleRef",
    "RoleSpec",
    # Core Models
    "Container",
    "ContainerPort",
    "CronJobSpec",
    "DaemonSetSpec",
    "DeploymentSpec",
    "EnvFromSource",
    "EnvVar",
    "PodSpec",
    "PodTemplateSpec",
    "Probe",
    "ResourceQuantity",
    "ResourceRequirements",
    "SecurityContext",
    "ServiceSpec",
    "ServicePort",
    "StatefulSetSpec",
    "Toleration",
    "Volume",
    "VolumeMount",
    # Core Builders
    "build_deployment",
    "build_service",
    "build_statefulset",
    "build_daemonset",
    "build_cronjob",
    "build_configmap",
    "build_secret",
    "build_hpa",
    "build_pdb",
    "build_serviceaccount",
    "build_namespace",
    # RBAC Builders
    "build_role",
    "build_clusterrole",
    "build_rolebinding",
    "build_clusterrolebinding",
    # Output
    "Manifest",
    "dump",
    "dump_one",
    "load",
    # Extensions
    "gke",
    # Validation
    "ValidationError",
    "ValidationMode",
    "ValidationResult",
    "validate_manifest",
]
