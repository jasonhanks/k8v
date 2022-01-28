import pytest
import io
import json
import munch

import k8v


class TestBriefFormatter:
    """Validate the BriefPrinter output for each resource type."""

    def setup(self):
        self.config = k8v.config.Config(colors=None, file=io.StringIO(""))
        self.config.load()
        self.printer = k8v.formatters.brief_formatter.BriefFormatter(self.config)
        # self.printer.config.colors = None  # disable colors for now
        # self.printer.begin()

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
        data = json.load(open("tests/fixtures/default-resources.json"))
        self.printer.begin_resource()
        for num, o in enumerate(data):
            resource = munch.munchify(o)  # convert dict() to an object
            resource.type = k8v.resource_types.ResourceType.from_value(
                resource.kind.lower()
            )
            self.printer.print(resource, "")
            self.printer.end_resource(num == len(data) - 1)

        # validate the printed output
        assert expected == self.config.file.getvalue()
