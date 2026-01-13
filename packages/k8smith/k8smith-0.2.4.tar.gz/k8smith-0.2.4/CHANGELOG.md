# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.4] - 2026-01-07

### Changes

- [FIX] Add missing hostPort and hostIP to ContainerPort (#4) (34af3d9)

## [0.2.3] - 2026-01-06

### Changes

- [DOCS] Remove GKE-specific content from general examples (#3) (5192c87)

## [0.2.2] - 2026-01-06

### Changes

- Merge pull request #2 from eliminyro/fix/author-name (a21f0fd)
- [FIX] Update author name in package metadata (ac53fe6)
- Merge pull request #1 from eliminyro/fix/release-token (7aa2eb8)
- [CI] Use RELEASE_TOKEN for protected branch push (1337c83)

## [0.2.1] - 2026-01-06

### Changes

- [FIX] Add docs build test to CI and fix documentation errors (840fd5a)

## [0.2.0] - 2026-01-06

### Changes

- [FEAT] Initial release - k8smith Kubernetes manifest generator (159b1a7)

- Core Kubernetes resources: Deployment, Service, StatefulSet, DaemonSet, CronJob, ConfigMap, Secret, HPA, PDB, ServiceAccount, Namespace
- RBAC resources: Role, ClusterRole, RoleBinding, ClusterRoleBinding
- GKE extensions: Gateway, HTTPRoute, HealthCheckPolicy, GCPBackendPolicy, PodMonitoring, ClusterPodMonitoring
- CSI volume support in `Volume` model for secrets-store and other CSI drivers
- `ResourceQuantity.extended` for custom resources like `nvidia.com/gpu`
- `Manifest` class for collecting and serializing multiple resources
- YAML output utilities with Kubernetes-friendly formatting
- Optional manifest validation
- Full type hints with py.typed marker