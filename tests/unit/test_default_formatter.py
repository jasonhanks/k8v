import pytest
import io
import json
import munch

import k8v


class TestDefaultFormatter:
    """Validate the BriefPrinter output for each resource type."""

    def setup(self):
        self.config = k8v.config.Config(colors=None, file=io.StringIO(""))
        self.config.load()
        self.viewer = k8v.viewer.Viewer(self.config)

        # these objects were unloaded using the tool to simulate a query to bring back each known type
        self.resources = []
        for num, o in enumerate(
            json.load(open("tests/fixtures/default-resources.json"))
        ):
            resource = munch.munchify(o)  # convert dict() to an object
            resource._related = []
            resource.type = k8v.resource_types.ResourceType.from_value(
                resource.kind.lower()
            )
            self.resources.append(resource)

    def test_output(self):
        """Validate the default resource fixtures are formatted correctly."""

        expected = """configmap/default/kube-root-ca.crt (data=[ca.crt])
configmap/default/nginx-cm (data=[ENV, app])
secret/default/default-token-5r2mb (data=[ca.crt, namespace, token])
secret/default/nginx-sec (data=[PASSWORD, USERNAME])
service/default/kubernetes (labels=[component=apiserver provider=kubernetes] type=ClusterIP cluster_ip=10.96.0.1 ports=[443=6443/TCP ])
replicaset/default/nginx-deployment-7b6fcd488c (labels=[app=nginx pod-template-hash=7b6fcd488c] replicas=2/2 avail=2 generation=1)
deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)
pod/default/list-resources-8xvpb (labels=[controller-uid=b3aa0bb1-708a-4ed0-bf59-f041024404d0 job-name=list-resources] sa=default )
pod/default/nginx-deployment-7b6fcd488c-5q8nt (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
pod/default/nginx-deployment-7b6fcd488c-7kdrw (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
cronjob/default/list-resources ()
job/default/list-resources (labels=[controller-uid=b3aa0bb1-708a-4ed0-bf59-f041024404d0 job-name=list-resources] )
persistentvolume/pvc-6801b99e-d658-4095-967b-b035c520886f (storage_class=standard access_modes=['ReadWriteOnce'] capacity=32Mi reclaim=Delete)
persistentvolumeclaim/default/nginx-pvc (access_modes=standard storage_class=['ReadWriteOnce'] capacity=32Mi volume=pvc-6801b99e-d658-4095-967b-b035c520886f phase=Bound)
"""

        for num, resource in enumerate(self.resources):
            self.viewer.print_resource(resource, num, len(self.resources) - 1, "")

        # validate the printed output
        assert self.config.file.getvalue() == expected

    def test_output_with_related(self):
        """Validate the default resource fixtures are formatted correctly with related resources."""

        expected = """configmap/default/kube-root-ca.crt (data=[ca.crt])
configmap/default/nginx-cm (data=[ENV, app])
secret/default/default-token-5r2mb (data=[ca.crt, namespace, token])
secret/default/nginx-sec (data=[PASSWORD, USERNAME])
service/default/kubernetes (labels=[component=apiserver provider=kubernetes] type=ClusterIP cluster_ip=10.96.0.1 ports=[443=6443/TCP ])
replicaset/default/nginx-deployment-7b6fcd488c (labels=[app=nginx pod-template-hash=7b6fcd488c] replicas=2/2 avail=2 generation=1)
        pod/default/nginx-deployment-7b6fcd488c-5q8nt (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
        pod/default/nginx-deployment-7b6fcd488c-7kdrw (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)
        replicaset/default/nginx-deployment-7b6fcd488c (labels=[app=nginx pod-template-hash=7b6fcd488c] replicas=2/2 avail=2 generation=1)
                pod/default/nginx-deployment-7b6fcd488c-5q8nt (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
                pod/default/nginx-deployment-7b6fcd488c-7kdrw (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
pod/default/list-resources-8xvpb (labels=[controller-uid=b3aa0bb1-708a-4ed0-bf59-f041024404d0 job-name=list-resources] sa=default )
pod/default/nginx-deployment-7b6fcd488c-5q8nt (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
pod/default/nginx-deployment-7b6fcd488c-7kdrw (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
cronjob/default/list-resources ()
job/default/list-resources (labels=[controller-uid=b3aa0bb1-708a-4ed0-bf59-f041024404d0 job-name=list-resources] )
persistentvolume/pvc-6801b99e-d658-4095-967b-b035c520886f (storage_class=standard access_modes=['ReadWriteOnce'] capacity=32Mi reclaim=Delete)
persistentvolumeclaim/default/nginx-pvc (access_modes=standard storage_class=['ReadWriteOnce'] capacity=32Mi volume=pvc-6801b99e-d658-4095-967b-b035c520886f phase=Bound)
"""

        # setup "related" resources to verify formatter output
        self.config.related = True
        self.resources[5]._related = [
            self.resources[8],
            self.resources[9],
        ]  # replicaset has pods
        self.resources[6]._related = [self.resources[5]]  # deployment has replicaset

        for num, resource in enumerate(self.resources):
            self.viewer.print_resource(resource, num, len(self.resources) - 1, "")

        # validate the printed output
        assert expected == self.config.file.getvalue()
