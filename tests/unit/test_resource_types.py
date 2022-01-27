import pytest

import k8v


class TestResourceTypes:
    """Validate various functionality related to the ResourceType behavior."""

    def test_from_value(self):
        """Validate that we can use all aliases for a known type."""

        # validate can support this for all known aliases for a specific type (will validate those value
        # possibilities for all types separately).
        for alias in k8v.resource_types.ResourceType.SERVICES.value:
            assert (
                k8v.resource_types.ResourceType.from_value(alias)
                == k8v.resource_types.ResourceType.SERVICES
            )

        # validate a random alias (non-default value)
        assert (
            k8v.resource_types.ResourceType.from_value("ingress")
            == k8v.resource_types.ResourceType.INGRESS
        )

        # Invalid values should be None
        assert k8v.resource_types.ResourceType.from_value(TestResourceTypes) == None
        assert k8v.resource_types.ResourceType.from_value(None) == None
        assert k8v.resource_types.ResourceType.from_value("") == None
        assert k8v.resource_types.ResourceType.from_value("configurationmap") == None
        assert k8v.resource_types.ResourceType.from_value("configurationmaps") == None

    def test_supported_types(self):
        """Validate the supported types by the viewer."""

        types = [t.value[0] for t in k8v.resource_types.ResourceType]
        types.sort()

        assert types == [
            "clusterrole",
            "clusterrolebinding",
            "configmap",
            "cronjob",
            "daemonset",
            "deployment",
            "ingress",
            "job",
            "networkpolicy",
            "persistentvolume",
            "persistentvolumeclaim",
            "pod",
            "replicaset",
            "role",
            "rolebinding",
            "secret",
            "service",
            "serviceaccount",
            "statefulset",
        ]

    def test_type_aliases(self):
        """Validate that aliases for the supported resource types are supported."""

        assert [x for x in k8v.resource_types.ResourceType.CLUSTER_ROLES.value] == [
            "clusterrole",
            "clusterroles",
        ]
        assert [
            x for x in k8v.resource_types.ResourceType.CLUSTER_ROLE_BINDINGS.value
        ] == ["clusterrolebinding", "clusterrolebindings"]
        assert [x for x in k8v.resource_types.ResourceType.ROLES.value] == [
            "role",
            "roles",
        ]
        assert [x for x in k8v.resource_types.ResourceType.ROLE_BINDINGS.value] == [
            "rolebinding",
            "rolebindings",
        ]
        assert [x for x in k8v.resource_types.ResourceType.CONFIG_MAP.value] == [
            "configmap",
            "configmaps",
            "cm",
            "cms",
        ]
        assert [x for x in k8v.resource_types.ResourceType.CRONJOBS.value] == [
            "cronjob",
            "cronjobs",
        ]
        assert [x for x in k8v.resource_types.ResourceType.DAEMON_SETS.value] == [
            "daemonset",
            "daemonsets",
            "ds",
        ]
        assert [x for x in k8v.resource_types.ResourceType.DEPLOYMENTS.value] == [
            "deployment",
            "deployments",
            "deploy",
            "deploys",
        ]
        assert [x for x in k8v.resource_types.ResourceType.INGRESS.value] == [
            "ingress",
            "ingresses",
            "ing",
        ]
        assert [x for x in k8v.resource_types.ResourceType.JOBS.value] == [
            "job",
            "jobs",
        ]
        assert [x for x in k8v.resource_types.ResourceType.NETWORK_POLICY.value] == [
            "networkpolicy",
            "networkpolicies",
            "netpol",
        ]
        assert [x for x in k8v.resource_types.ResourceType.PERSISTENT_VOLUME.value] == [
            "persistentvolume",
            "persistentvolumes",
            "pv",
        ]
        assert [
            x for x in k8v.resource_types.ResourceType.PERSISTENT_VOLUME_CLAIM.value
        ] == ["persistentvolumeclaim", "persistentvolumeclaims", "pvc"]
        assert [x for x in k8v.resource_types.ResourceType.PODS.value] == [
            "pod",
            "pods",
            "po",
        ]
        assert [x for x in k8v.resource_types.ResourceType.REPLICA_SETS.value] == [
            "replicaset",
            "replicasets",
            "rs",
        ]
        assert [x for x in k8v.resource_types.ResourceType.ROLES.value] == [
            "role",
            "roles",
        ]
        assert [x for x in k8v.resource_types.ResourceType.ROLE_BINDINGS.value] == [
            "rolebinding",
            "rolebindings",
        ]
        assert [x for x in k8v.resource_types.ResourceType.SECRETS.value] == [
            "secret",
            "secrets",
        ]
        assert [x for x in k8v.resource_types.ResourceType.SERVICES.value] == [
            "service",
            "services",
            "svc",
            "svcs",
        ]
        assert [x for x in k8v.resource_types.ResourceType.SERVICE_ACCOUNTS.value] == [
            "serviceaccount",
            "serviceaccounts",
            "sa",
        ]
        assert [x for x in k8v.resource_types.ResourceType.STATEFUL_SETS.value] == [
            "statefulset",
            "statefulsets",
            "sts",
        ]
