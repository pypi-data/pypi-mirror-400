"""Tests for Deployment builder."""

from k8smith import (
    Container,
    DeploymentSpec,
    PodSpec,
    PodTemplateSpec,
    ResourceQuantity,
    ResourceRequirements,
    Volume,
    VolumeMount,
    build_deployment,
)


class TestBuildDeployment:
    """Tests for build_deployment function."""

    def test_minimal_deployment(self):
        """Test building a minimal deployment."""
        spec = DeploymentSpec(
            name="test-app",
            namespace="default",
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="test-app", image="nginx:latest")])
            ),
        )

        result = build_deployment(spec)

        assert result["apiVersion"] == "apps/v1"
        assert result["kind"] == "Deployment"
        assert result["metadata"]["name"] == "test-app"
        assert result["metadata"]["namespace"] == "default"
        # replicas is omitted when not specified (K8s defaults to 1 server-side)
        assert "replicas" not in result["spec"]
        assert len(result["spec"]["template"]["spec"]["containers"]) == 1

    def test_deployment_no_extra_fields(self):
        """Ensure no hidden defaults like hostNetwork: false."""
        spec = DeploymentSpec(
            name="test",
            namespace="default",
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="test", image="nginx")])
            ),
        )

        result = build_deployment(spec)

        # These should NOT be present unless explicitly set
        pod_spec = result["spec"]["template"]["spec"]
        assert "hostNetwork" not in pod_spec
        assert "minReadySeconds" not in result["spec"]
        container = pod_spec["containers"][0]
        assert "startupProbe" not in container

    def test_deployment_with_resources(self):
        """Test deployment with resource requests and limits."""
        spec = DeploymentSpec(
            name="web",
            namespace="production",
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

        result = build_deployment(spec)
        resources = result["spec"]["template"]["spec"]["containers"][0]["resources"]

        assert resources["requests"]["cpu"] == "100m"
        assert resources["requests"]["memory"] == "128Mi"
        assert resources["limits"]["memory"] == "256Mi"
        assert "cpu" not in resources["limits"]

    def test_deployment_with_gpu(self):
        """Test extended resources like nvidia.com/gpu."""
        spec = DeploymentSpec(
            name="gpu-app",
            namespace="ml",
            template=PodTemplateSpec(
                spec=PodSpec(
                    containers=[
                        Container(
                            name="gpu-app",
                            image="ml:v1",
                            resources=ResourceRequirements(
                                limits=ResourceQuantity(
                                    memory="8Gi",
                                    extended={"nvidia.com/gpu": "1"},
                                ),
                            ),
                        )
                    ]
                )
            ),
        )

        result = build_deployment(spec)
        resources = result["spec"]["template"]["spec"]["containers"][0]["resources"]

        assert resources["limits"]["memory"] == "8Gi"
        assert resources["limits"]["nvidia.com/gpu"] == "1"

    def test_deployment_with_labels_and_annotations(self):
        """Test deployment with labels and annotations."""
        spec = DeploymentSpec(
            name="web",
            namespace="production",
            labels={"app": "web", "team": "platform"},
            annotations={"description": "Web server"},
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="web", image="nginx")])
            ),
        )

        result = build_deployment(spec)

        assert result["metadata"]["labels"]["app"] == "web"
        assert result["metadata"]["labels"]["team"] == "platform"
        assert result["metadata"]["annotations"]["description"] == "Web server"

    def test_deployment_selector_in_pod_labels(self):
        """Test that selector labels are included in pod labels."""
        spec = DeploymentSpec(
            name="web",
            namespace="production",
            selector={"app": "web"},
            template=PodTemplateSpec(
                metadata={"labels": {"version": "v1"}},
                spec=PodSpec(containers=[Container(name="web", image="nginx")]),
            ),
        )

        result = build_deployment(spec)

        # Selector should be in matchLabels
        assert result["spec"]["selector"]["matchLabels"] == {"app": "web"}

        # Pod labels should include both selector and template labels
        pod_labels = result["spec"]["template"]["metadata"]["labels"]
        assert pod_labels["app"] == "web"
        assert pod_labels["version"] == "v1"

    def test_deployment_with_replicas(self):
        """Test deployment with custom replica count."""
        spec = DeploymentSpec(
            name="web",
            namespace="production",
            replicas=5,
            template=PodTemplateSpec(
                spec=PodSpec(containers=[Container(name="web", image="nginx")])
            ),
        )

        result = build_deployment(spec)

        assert result["spec"]["replicas"] == 5

    def test_deployment_with_csi_volume(self):
        """Test deployment with CSI volume (e.g., secrets-store)."""
        spec = DeploymentSpec(
            name="app",
            namespace="production",
            template=PodTemplateSpec(
                spec=PodSpec(
                    containers=[
                        Container(
                            name="app",
                            image="myapp:v1",
                            volume_mounts=[
                                VolumeMount(
                                    name="secrets",
                                    mount_path="/mnt/secrets",
                                    read_only=True,
                                )
                            ],
                        )
                    ],
                    volumes=[
                        Volume(
                            name="secrets",
                            csi={
                                "driver": "secrets-store.csi.k8s.io",
                                "readOnly": True,
                                "volumeAttributes": {"secretProviderClass": "my-secrets"},
                            },
                        )
                    ],
                )
            ),
        )

        result = build_deployment(spec)

        volumes = result["spec"]["template"]["spec"]["volumes"]
        assert len(volumes) == 1
        assert volumes[0]["name"] == "secrets"
        assert volumes[0]["csi"]["driver"] == "secrets-store.csi.k8s.io"
        assert volumes[0]["csi"]["readOnly"] is True
        assert volumes[0]["csi"]["volumeAttributes"]["secretProviderClass"] == "my-secrets"

        # Verify volume mount
        mounts = result["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
        assert len(mounts) == 1
        assert mounts[0]["name"] == "secrets"
        assert mounts[0]["mountPath"] == "/mnt/secrets"
