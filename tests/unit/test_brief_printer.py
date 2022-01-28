import pytest
import io
import json
import munch
import yaml

import k8v


class TestBriefPrinter:
    """Validate the BriefPrinter output for each resource type."""

    def setup(self):
        self.viewer: Viewer = k8v.viewer.Viewer(k8v.config.Config())
        self.viewer.config.colors = None  # disable colors for now
        self.viewer.config.output = "brief"
        self.viewer.config.file = io.StringIO("")  # store output in StringIO
        self.viewer.setup()

    def test_output(self):
        """Validate the format of each known type we load from tests/manifests/default-resources.json."""

        expected = """configmap/default/kube-root-ca.crt
configmap/default/nginx-cm
secret/default/default-token-5r2mb
secret/default/nginx-sec
service/default/kubernetes
replicaset/default/nginx-deployment-7b6fcd488c
deployment/default/nginx-deployment
pod/default/nginx-deployment-7b6fcd488c-5q8nt
pod/default/nginx-deployment-7b6fcd488c-7kdrw
persistentvolume/pvc-6801b99e-d658-4095-967b-b035c520886f
persistentvolumeclaim/default/nginx-pvc
"""

        # these objects were unloaded using the tool to simulate a query to bring back each known type
        for o in json.load(open("tests/fixtures/default-resources.json")):
            resource = munch.munchify(o)  # convert dict() to an object
            resource.type = k8v.resource_types.ResourceType.from_value(
                resource.kind.lower()
            )
            self.viewer.printer.print(resource, delim="")

        # validate the printed output
        assert expected == self.viewer.config.file.getvalue()
