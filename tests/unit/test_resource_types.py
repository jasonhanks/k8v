import pytest

import k8v

def test_supported_types():
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
