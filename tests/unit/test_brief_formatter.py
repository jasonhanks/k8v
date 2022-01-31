import pytest
import io
import json
import munch

import k8v


class TestBriefFormatter:
    """Validate the BriefPrinter output for each resource type."""

    def setup(self):
        self.config = k8v.config.Config(
            colors=None, file=io.StringIO(""), output="brief"
        )
        self.config.load()
        self.viewer = k8v.viewer.Viewer(self.config)
        self.printer = k8v.formatters.brief_formatter.BriefFormatter(self.config)

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

        expected = """configmap/default/kube-root-ca.crt
configmap/default/nginx-cm
secret/default/default-token-5r2mb
secret/default/nginx-sec
service/default/kubernetes
replicaset/default/nginx-deployment-7b6fcd488c
deployment/default/nginx-deployment
pod/default/list-resources-8xvpb
pod/default/nginx-deployment-7b6fcd488c-5q8nt
pod/default/nginx-deployment-7b6fcd488c-7kdrw
cronjob/default/list-resources
job/default/list-resources
persistentvolume/pvc-6801b99e-d658-4095-967b-b035c520886f
persistentvolumeclaim/default/nginx-pvc
"""

        for num, resource in enumerate(self.resources):
            self.viewer.print_resource(resource, num, len(self.resources) - 1, "")

        # validate the printed output
        assert expected == self.config.file.getvalue()

    def test_output_with_related(self):
        """Validate the default resource fixtures are formatted correctly with related resources."""

        expected = """configmap/default/kube-root-ca.crt
configmap/default/nginx-cm
secret/default/default-token-5r2mb
secret/default/nginx-sec
service/default/kubernetes
replicaset/default/nginx-deployment-7b6fcd488c
        pod/default/list-resources-8xvpb
        pod/default/nginx-deployment-7b6fcd488c-5q8nt
deployment/default/nginx-deployment
        replicaset/default/nginx-deployment-7b6fcd488c
                pod/default/list-resources-8xvpb
                pod/default/nginx-deployment-7b6fcd488c-5q8nt
pod/default/list-resources-8xvpb
pod/default/nginx-deployment-7b6fcd488c-5q8nt
pod/default/nginx-deployment-7b6fcd488c-7kdrw
cronjob/default/list-resources
job/default/list-resources
persistentvolume/pvc-6801b99e-d658-4095-967b-b035c520886f
persistentvolumeclaim/default/nginx-pvc
"""

        # setup "related" resources to verify formatter output
        self.config.related = True
        self.resources[5]._related = [
            self.resources[7],
            self.resources[8],
        ]  # replicaset has pods
        self.resources[6]._related = [self.resources[5]]  # deployment has replicaset

        for num, resource in enumerate(self.resources):
            self.viewer.print_resource(resource, num, len(self.resources) - 1, "")

        # validate the printed output
        assert expected == self.config.file.getvalue()
