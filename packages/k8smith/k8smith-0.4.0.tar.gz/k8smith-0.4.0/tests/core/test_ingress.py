"""Tests for Ingress builder."""

from k8smith import (
    IngressBackend,
    IngressRule,
    IngressSpec,
    IngressTLS,
    build_ingress,
)


class TestBuildIngress:
    """Tests for build_ingress function."""

    def test_minimal_ingress(self):
        """Test building a minimal ingress with single rule."""
        spec = IngressSpec(
            name="web-ingress",
            namespace="production",
            rules=[
                IngressRule(
                    host="example.com",
                    http={
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {"service": {"name": "web", "port": {"number": 80}}},
                            }
                        ]
                    },
                )
            ],
        )

        result = build_ingress(spec)

        assert result["apiVersion"] == "networking.k8s.io/v1"
        assert result["kind"] == "Ingress"
        assert result["metadata"]["name"] == "web-ingress"
        assert result["metadata"]["namespace"] == "production"
        assert len(result["spec"]["rules"]) == 1
        assert result["spec"]["rules"][0]["host"] == "example.com"

    def test_ingress_no_extra_fields(self):
        """Ensure no hidden defaults are added."""
        spec = IngressSpec(
            name="test",
            namespace="default",
            rules=[
                IngressRule(
                    host="test.com",
                    http={"paths": []},
                )
            ],
        )

        result = build_ingress(spec)

        # These should NOT be present unless explicitly set
        assert "ingressClassName" not in result["spec"]
        assert "defaultBackend" not in result["spec"]
        assert "tls" not in result["spec"]

    def test_ingress_with_tls(self):
        """Test ingress with TLS configuration."""
        spec = IngressSpec(
            name="secure-ingress",
            namespace="production",
            tls=[IngressTLS(hosts=["example.com", "www.example.com"], secret_name="tls-secret")],
            rules=[
                IngressRule(
                    host="example.com",
                    http={
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {"service": {"name": "web", "port": {"number": 80}}},
                            }
                        ]
                    },
                )
            ],
        )

        result = build_ingress(spec)

        assert len(result["spec"]["tls"]) == 1
        assert result["spec"]["tls"][0]["hosts"] == ["example.com", "www.example.com"]
        assert result["spec"]["tls"][0]["secretName"] == "tls-secret"

    def test_ingress_with_ingress_class_name(self):
        """Test ingress with ingressClassName."""
        spec = IngressSpec(
            name="web-ingress",
            namespace="production",
            ingress_class_name="my-ingress-class",
            rules=[
                IngressRule(
                    host="example.com",
                    http={"paths": []},
                )
            ],
        )

        result = build_ingress(spec)

        assert result["spec"]["ingressClassName"] == "my-ingress-class"

    def test_ingress_with_default_backend(self):
        """Test ingress with defaultBackend."""
        spec = IngressSpec(
            name="fallback-ingress",
            namespace="production",
            default_backend=IngressBackend(
                service={"name": "fallback-service", "port": {"number": 80}}
            ),
        )

        result = build_ingress(spec)

        assert result["spec"]["defaultBackend"]["service"]["name"] == "fallback-service"
        assert result["spec"]["defaultBackend"]["service"]["port"]["number"] == 80

    def test_ingress_with_multiple_hosts(self):
        """Test ingress with multiple host rules."""
        spec = IngressSpec(
            name="multi-host-ingress",
            namespace="production",
            rules=[
                IngressRule(
                    host="api.example.com",
                    http={
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {"service": {"name": "api", "port": {"number": 8080}}},
                            }
                        ]
                    },
                ),
                IngressRule(
                    host="admin.example.com",
                    http={
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {"service": {"name": "admin", "port": {"number": 3000}}},
                            }
                        ]
                    },
                ),
            ],
        )

        result = build_ingress(spec)

        assert len(result["spec"]["rules"]) == 2
        assert result["spec"]["rules"][0]["host"] == "api.example.com"
        assert result["spec"]["rules"][1]["host"] == "admin.example.com"

    def test_ingress_with_multiple_paths(self):
        """Test ingress with multiple paths on single host."""
        spec = IngressSpec(
            name="multi-path-ingress",
            namespace="production",
            rules=[
                IngressRule(
                    host="example.com",
                    http={
                        "paths": [
                            {
                                "path": "/api",
                                "pathType": "Prefix",
                                "backend": {"service": {"name": "api", "port": {"number": 8080}}},
                            },
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {"name": "frontend", "port": {"number": 80}}
                                },
                            },
                        ]
                    },
                )
            ],
        )

        result = build_ingress(spec)

        paths = result["spec"]["rules"][0]["http"]["paths"]
        assert len(paths) == 2
        assert paths[0]["path"] == "/api"
        assert paths[1]["path"] == "/"

    def test_ingress_with_labels_and_annotations(self):
        """Test ingress with labels and annotations."""
        spec = IngressSpec(
            name="web-ingress",
            namespace="production",
            labels={"app": "web", "env": "production"},
            annotations={"cert-manager.io/cluster-issuer": "letsencrypt-prod"},
            rules=[IngressRule(host="example.com", http={"paths": []})],
        )

        result = build_ingress(spec)

        assert result["metadata"]["labels"] == {"app": "web", "env": "production"}
        assert result["metadata"]["annotations"] == {
            "cert-manager.io/cluster-issuer": "letsencrypt-prod"
        }
