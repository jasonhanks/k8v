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

    def test_configmap(self):
        pass

    def test_output(self):
        """Validate the default resource fixtures are formatted correctly."""

        expected = """configmap/default/kube-root-ca.crt
configmap/default/nginx-cm
cronjob/default/list-resources
deployment/default/nginx-deployment
job/default/list-resources
persistentvolumeclaim/default/nginx-pvc
pod/default/list-resources-8xvpb
pod/default/nginx-deployment-7b6fcd488c-5q8nt
pod/default/nginx-deployment-7b6fcd488c-7kdrw
replicaset/default/nginx-deployment-7b6fcd488c
secret/default/default-token-5r2mb
secret/default/nginx-sec
service/default/kubernetes
"""

        for num, resource in enumerate(self.resources):
            self.viewer.print_resource(resource, num, len(self.resources) - 1, "")

        assert self.config.file.getvalue() == expected

    def test_output_with_related(self):
        """Validate the default resource fixtures are formatted correctly with related resources."""

        expected = """configmap/default/kube-root-ca.crt
configmap/default/nginx-cm
cronjob/default/list-resources
deployment/default/nginx-deployment
        replicaset/default/nginx-deployment-7b6fcd488c
                pod/default/nginx-deployment-7b6fcd488c-5q8nt
                pod/default/nginx-deployment-7b6fcd488c-7kdrw
job/default/list-resources
persistentvolumeclaim/default/nginx-pvc
pod/default/list-resources-8xvpb
pod/default/nginx-deployment-7b6fcd488c-5q8nt
pod/default/nginx-deployment-7b6fcd488c-7kdrw
replicaset/default/nginx-deployment-7b6fcd488c
        pod/default/nginx-deployment-7b6fcd488c-5q8nt
        pod/default/nginx-deployment-7b6fcd488c-7kdrw
secret/default/default-token-5r2mb
secret/default/nginx-sec
service/default/kubernetes
"""

        # setup "related" resources to verify formatter output
        self.config.related = True
        self.resources[9]._related = [
            self.resources[7],
            self.resources[8],
        ]  # replicaset has pods
        self.resources[3]._related = [self.resources[9]]  # deployment has replicaset

        for num, resource in enumerate(self.resources):
            self.viewer.print_resource(resource, num, len(self.resources) - 1, "")

        lines = self.config.file.getvalue().split("\n")
        for num, expect in enumerate(expected.split("\n")):
            assert expect == lines[num]
