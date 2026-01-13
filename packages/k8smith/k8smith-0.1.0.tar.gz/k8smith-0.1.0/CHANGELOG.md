# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-05

### Added

- Core Kubernetes resources: Deployment, Service, StatefulSet, DaemonSet, CronJob, ConfigMap, Secret, HPA, PDB, ServiceAccount, Namespace, Role, ClusterRole, RoleBinding, ClusterRoleBinding
- GKE extensions: Gateway, HTTPRoute, HealthCheckPolicy, GCPBackendPolicy, PodMonitoring, ClusterPodMonitoring
- `ResourceQuantity.extended` for custom resources like `nvidia.com/gpu`
- `Manifest` class for collecting and serializing multiple resources
- YAML output utilities with Kubernetes-friendly formatting
- Optional manifest validation
- Full type hints with py.typed marker
