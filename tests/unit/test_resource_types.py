import pytest

import k8v


class TestResourceTypes:
    """Validate various functionality related to the ResourceType behavior."""

    def setup(self) -> None:
        self.expected_types = {
            k8v.resource_types.ResourceType.CLUSTER_ROLES: [
                "clusterrole",
                "clusterroles",
            ],
            k8v.resource_types.ResourceType.CLUSTER_ROLE_BINDINGS: [
                "clusterrolebinding",
                "clusterrolebindings",
            ],
            k8v.resource_types.ResourceType.CONFIG_MAP: [
                "configmap",
                "configmaps",
                "cm",
                "cms",
            ],
            k8v.resource_types.ResourceType.CRONJOBS: [
                "cronjob",
                "cronjobs",
            ],
            k8v.resource_types.ResourceType.DAEMON_SETS: [
                "daemonset",
                "daemonsets",
                "ds",
            ],
            k8v.resource_types.ResourceType.DEPLOYMENTS: [
                "deployment",
                "deployments",
                "deploy",
                "deploys",
            ],
            k8v.resource_types.ResourceType.INGRESS: [
                "ingress",
                "ingresses",
                "ing",
            ],
            k8v.resource_types.ResourceType.JOBS: [
                "job",
                "jobs",
            ],
            k8v.resource_types.ResourceType.NETWORK_POLICY: [
                "networkpolicy",
                "networkpolicies",
                "netpol",
            ],
            k8v.resource_types.ResourceType.PERSISTENT_VOLUME: [
                "persistentvolume",
                "persistentvolumes",
                "pv",
            ],
            k8v.resource_types.ResourceType.PERSISTENT_VOLUME_CLAIM: [
                "persistentvolumeclaim",
                "persistentvolumeclaims",
                "pvc",
            ],
            k8v.resource_types.ResourceType.PODS: [
                "pod",
                "pods",
                "po",
            ],
            k8v.resource_types.ResourceType.REPLICA_SETS: [
                "replicaset",
                "replicasets",
                "rs",
            ],
            k8v.resource_types.ResourceType.ROLES: [
                "role",
                "roles",
            ],
            k8v.resource_types.ResourceType.ROLE_BINDINGS: [
                "rolebinding",
                "rolebindings",
            ],
            k8v.resource_types.ResourceType.SECRETS: [
                "secret",
                "secrets",
            ],
            k8v.resource_types.ResourceType.SERVICES: [
                "service",
                "services",
                "svc",
                "svcs",
            ],
            k8v.resource_types.ResourceType.SERVICE_ACCOUNTS: [
                "serviceaccount",
                "serviceaccounts",
                "sa",
            ],
            k8v.resource_types.ResourceType.STATEFUL_SETS: [
                "statefulset",
                "statefulsets",
                "sts",
            ],
        }

    def test_from_value_valid(self) -> None:
        """Validate that we can use all aliases for a known type."""
        for t, aliases in self.expected_types.items():
            for alias in aliases:
                assert k8v.resource_types.ResourceType.from_value(alias) == t

    def test_from_value_invalid(self) -> None:
        """Validate that we cannot use an invalid alias."""
        assert k8v.resource_types.ResourceType.from_value(TestResourceTypes) == None
        assert k8v.resource_types.ResourceType.from_value(None) == None
        assert k8v.resource_types.ResourceType.from_value(True) == None
        assert k8v.resource_types.ResourceType.from_value(False) == None
        assert k8v.resource_types.ResourceType.from_value("") == None
        assert k8v.resource_types.ResourceType.from_value("configurationmap") == None
        assert k8v.resource_types.ResourceType.from_value("configurationmaps") == None

    def test_supported_types(self) -> None:
        """Validate the supported types by the viewer."""
        types = [t.value[0] for t in k8v.resource_types.ResourceType]
        types.sort()
        assert types == [x[0] for x in self.expected_types.values()]

    def test_type_aliases(self) -> None:
        """Validate that aliases for the supported resource types are supported."""
        for type, aliases in self.expected_types.items():
            for alias in aliases:
                assert alias in type.value
