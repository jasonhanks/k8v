import enum


class ResourceType(enum.Enum):
    """Definitions of the various resource types that can be displayed."""

    # CoreV1Api
    CONFIG_MAP = ["configmap", "configmaps", "cm", "cms"]
    PERSISTENT_VOLUME = ["persistentvolume", "persistentvolumes", "pv"]
    PERSISTENT_VOLUME_CLAIM = ["persistentvolumeclaim", "persistentvolumeclaims", "pvc"]
    PODS = ["pod", "pods", "po"]
    SECRETS = ["secret", "secrets"]
    SERVICES = ["service", "services", "svc", "svcs"]
    SERVICE_ACCOUNTS = ["serviceaccount", "serviceaccounts", "sa"]

    # AppsV1Api
    REPLICA_SETS = ["replicaset", "replicasets", "rs"]
    DAEMON_SETS = ["daemonset", "daemonsets", "ds"]
    STATEFUL_SETS = ["statefulset", "statefulsets", "sts"]
    DEPLOYMENTS = ["deployment", "deployments", "deploy", "deploys"]

    # BatchV1Api
    JOBS = ["job", "jobs"]
    CRONJOBS = ["cronjob", "cronjobs"]

    # NetworkingV1Api
    INGRESS = ["ingress", "ingresses", "ing"]
    NETWORK_POLICY = ["networkpolicy", "networkpolicies", "netpol"]

    # RbacAuthorizationV1Api
    CLUSTER_ROLES = ["clusterrole", "clusterroles"]
    CLUSTER_ROLE_BINDINGS = ["clusterrolebinding", "clusterrolebindings"]
    ROLES = ["role", "roles"]
    ROLE_BINDINGS = ["rolebinding", "rolebindings"]

    @staticmethod
    def from_value(value):
        for type in ResourceType:
            if value in type.value:
                return type
        return None
