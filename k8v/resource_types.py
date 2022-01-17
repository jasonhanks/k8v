import enum


class ResourceType(enum.Enum):
    """Definitions of the various resource types that can be displayed."""

    # configuration
    CONFIG_MAP  = ["configmap", "configmaps", "cm", "cms"]
    SECRETS     = ["secret", "secrets"]

    # workloads
    SERVICES    = ["service", "services", "svc", "svcs"]
    INGRESS     = ["ingress", "ingresses", "ing"]
    REPLICA_SETS = ["replicaset", "replicasets", "rs"]
    DAEMON_SETS = ["daemonset", "daemonsets", "ds"]
    DEPLOYMENTS = ["deployment", "deployments", "deploy", "deploys"]
    PODS        = ["pod", "pods", "po"]

    # volumes
    PERSISTENT_VOLUME = ["persistentvolume", "persistentvolumes", "pv"]
    PERSISTENT_VOLUME_CLAIM = ["persistentvolumeclaim", "persistentvolumeclaims", "pvc"]
