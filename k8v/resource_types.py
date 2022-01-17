import enum


class ResourceType(enum.Enum):
    """Definitions of the various resource types that can be displayed."""

    # configuration
    CONFIG_MAP  = ["configmap", "configmaps", "cm", "cms"]
    SECRETS     = ["secret", "secrets"]

    # workloads
    REPLICA_SETS = ["replicaset", "replicasets", "rs"]
    DAEMON_SETS = ["daemonset", "daemonsets", "ds"]
    DEPLOYMENTS = ["deployment", "deployments", "deploy", "deploys"]
    SERVICES    = ["service", "services", "svc", "svcs"]
    PODS        = ["pod", "pods", "po"]
    INGRESS     = ["ingress", "ingresses", "ing"]
