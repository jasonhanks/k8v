import enum


class ResourceType(enum.Enum):
    """Definitions of the various resource types that can be displayed."""

    CONFIG_MAP = ["configmap", "configmaps", "cm", "cms"]
    CLUSTER_ROLES = ["clusterrole", "clusterroles"]
    CLUSTER_ROLE_BINDINGS = ["clusterrolebinding", "clusterrolebindings"]
    CRONJOBS = ["cronjob", "cronjobs"]
    DAEMON_SETS = ["daemonset", "daemonsets", "ds"]
    DEPLOYMENTS = ["deployment", "deployments", "deploy", "deploys"]
    INGRESS = ["ingress", "ingresses", "ing"]
    JOBS = ["job", "jobs"]
    NETWORK_POLICY = ["networkpolicy", "networkpolicies", "netpol"]
    PERSISTENT_VOLUME = ["persistentvolume", "persistentvolumes", "pv"]
    PERSISTENT_VOLUME_CLAIM = ["persistentvolumeclaim", "persistentvolumeclaims", "pvc"]
    PODS = ["pod", "pods", "po"]
    REPLICA_SETS = ["replicaset", "replicasets", "rs"]
    ROLES = ["role", "roles"]
    ROLE_BINDINGS = ["rolebinding", "rolebindings"]
    SECRETS = ["secret", "secrets"]
    SERVICES = ["service", "services", "svc", "svcs"]
    SERVICE_ACCOUNTS = ["serviceaccount", "serviceaccounts", "sa"]
    STATEFUL_SETS = ["statefulset", "statefulsets", "sts"]

    @staticmethod
    def from_value(value):
        for type in ResourceType:
            if value in type.value:
                return type
        return None
