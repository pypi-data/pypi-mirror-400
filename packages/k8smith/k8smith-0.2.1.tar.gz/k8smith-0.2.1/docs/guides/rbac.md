# RBAC

k8smith provides full support for Kubernetes Role-Based Access Control (RBAC) resources.

## Roles and ClusterRoles

### Namespace-scoped Role

```python
from k8smith import RoleSpec, PolicyRule, build_role

role = build_role(
    RoleSpec(
        name="pod-reader",
        namespace="default",
        rules=[
            PolicyRule(
                api_groups=[""],
                resources=["pods"],
                verbs=["get", "watch", "list"],
            ),
        ],
    )
)
```

### Cluster-scoped ClusterRole

```python
from k8smith import ClusterRoleSpec, PolicyRule, build_clusterrole

cluster_role = build_clusterrole(
    ClusterRoleSpec(
        name="node-reader",
        rules=[
            PolicyRule(
                api_groups=[""],
                resources=["nodes"],
                verbs=["get", "watch", "list"],
            ),
        ],
    )
)
```

### Multiple Rules

```python
cluster_role = build_clusterrole(
    ClusterRoleSpec(
        name="deployment-manager",
        rules=[
            PolicyRule(
                api_groups=["apps"],
                resources=["deployments"],
                verbs=["get", "list", "watch", "create", "update", "patch", "delete"],
            ),
            PolicyRule(
                api_groups=[""],
                resources=["pods", "pods/log"],
                verbs=["get", "list", "watch"],
            ),
            PolicyRule(
                api_groups=[""],
                resources=["configmaps", "secrets"],
                verbs=["get", "list"],
            ),
        ],
    )
)
```

## RoleBindings and ClusterRoleBindings

### Binding a Role to a User

```python
from k8smith import (
    RoleBindingSpec,
    RoleBindingSubject,
    RoleRef,
    build_rolebinding,
)

binding = build_rolebinding(
    RoleBindingSpec(
        name="read-pods",
        namespace="default",
        subjects=[
            RoleBindingSubject(
                kind="User",
                name="jane@example.com",
                api_group="rbac.authorization.k8s.io",
            ),
        ],
        role_ref=RoleRef(
            kind="Role",
            name="pod-reader",
        ),
    )
)
```

### Binding a ClusterRole to a ServiceAccount

```python
from k8smith import (
    ClusterRoleBindingSpec,
    RoleBindingSubject,
    RoleRef,
    build_clusterrolebinding,
)

binding = build_clusterrolebinding(
    ClusterRoleBindingSpec(
        name="monitoring-view",
        subjects=[
            RoleBindingSubject(
                kind="ServiceAccount",
                name="prometheus",
                namespace="monitoring",
            ),
        ],
        role_ref=RoleRef(
            kind="ClusterRole",
            name="view",
        ),
    )
)
```

### Binding to a Group

```python
binding = build_clusterrolebinding(
    ClusterRoleBindingSpec(
        name="admin-group",
        subjects=[
            RoleBindingSubject(
                kind="Group",
                name="system:admins",
                api_group="rbac.authorization.k8s.io",
            ),
        ],
        role_ref=RoleRef(
            kind="ClusterRole",
            name="cluster-admin",
        ),
    )
)
```

## Complete Example

Here's a complete example setting up RBAC for an application:

```python
from k8smith import (
    Manifest,
    ServiceAccountSpec,
    RoleSpec,
    RoleBindingSpec,
    PolicyRule,
    RoleBindingSubject,
    RoleRef,
    build_serviceaccount,
    build_role,
    build_rolebinding,
)

NAMESPACE = "myapp"
APP_NAME = "worker"

manifest = Manifest()

# Create ServiceAccount
manifest.add(
    build_serviceaccount(
        ServiceAccountSpec(
            name=APP_NAME,
            namespace=NAMESPACE,
        )
    )
)

# Create Role with required permissions
manifest.add(
    build_role(
        RoleSpec(
            name=f"{APP_NAME}-role",
            namespace=NAMESPACE,
            rules=[
                PolicyRule(
                    api_groups=[""],
                    resources=["configmaps"],
                    verbs=["get", "list", "watch"],
                ),
                PolicyRule(
                    api_groups=[""],
                    resources=["secrets"],
                    resource_names=[f"{APP_NAME}-secrets"],
                    verbs=["get"],
                ),
            ],
        )
    )
)

# Bind Role to ServiceAccount
manifest.add(
    build_rolebinding(
        RoleBindingSpec(
            name=f"{APP_NAME}-rolebinding",
            namespace=NAMESPACE,
            subjects=[
                RoleBindingSubject(
                    kind="ServiceAccount",
                    name=APP_NAME,
                    namespace=NAMESPACE,
                ),
            ],
            role_ref=RoleRef(
                kind="Role",
                name=f"{APP_NAME}-role",
            ),
        )
    )
)

print(manifest.to_yaml())
```

## Common Patterns

### Read-only access to a namespace

```python
role = build_role(
    RoleSpec(
        name="namespace-viewer",
        namespace="production",
        rules=[
            PolicyRule(
                api_groups=["", "apps", "batch"],
                resources=["*"],
                verbs=["get", "list", "watch"],
            ),
        ],
    )
)
```

### CI/CD deployment permissions

```python
role = build_role(
    RoleSpec(
        name="deployer",
        namespace="production",
        rules=[
            PolicyRule(
                api_groups=["apps"],
                resources=["deployments", "statefulsets", "daemonsets"],
                verbs=["get", "list", "watch", "create", "update", "patch"],
            ),
            PolicyRule(
                api_groups=[""],
                resources=["services", "configmaps"],
                verbs=["get", "list", "watch", "create", "update", "patch"],
            ),
            PolicyRule(
                api_groups=["networking.k8s.io"],
                resources=["ingresses"],
                verbs=["get", "list", "watch", "create", "update", "patch"],
            ),
        ],
    )
)
```
