import pytest
import io
import re

import k8v


class TestResourceFilters:
    def setup(self):
        self.viewer: Viewer = k8v.viewer.Viewer(k8v.config.Config())
        self.viewer.config.colors = None  # disable colors for now
        self.viewer.config.file = io.StringIO("")  # store output in StringIO

    def test_filter_configmaps(self):
        self.viewer.config.resources.append(k8v.resource_types.ResourceType.CONFIG_MAP)
        self.viewer.view()
        lines = self.viewer.config.file.getvalue().split("\n")
        assert len(lines) == 3
        assert lines[0] == "configmap/default/kube-root-ca.crt (data=[ca.crt])"
        assert lines[1] == "configmap/default/nginx-cm (data=[ENV, app])"
        assert lines[2] == ""

    def test_filter_deployment(self):
        self.viewer.config.resources.append(k8v.resource_types.ResourceType.DEPLOYMENTS)
        self.viewer.view()
        lines = self.viewer.config.file.getvalue().split("\n")
        assert len(lines) == 2
        assert (
            lines[0]
            == "deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)"
        )
        assert lines[1] == ""

    def test_filter_pvc(self):
        self.viewer.config.resources.append(
            k8v.resource_types.ResourceType.PERSISTENT_VOLUME_CLAIM
        )
        self.viewer.view()
        lines = self.viewer.config.file.getvalue().split("\n")
        assert len(lines) == 2
        m = re.search(
            r"persistentvolumeclaim/default/nginx-pvc \(access_modes=standard storage_class=\['ReadWriteOnce'\] capacity=32Mi volume=(.*) phase=Bound\)",
            lines[0],
        )
        assert m != None
        assert m.group(0) == lines[0]
        assert m.group(1) is not None
        assert lines[1] == ""

    def test_filter_secrets(self):
        self.viewer.config.resources.append(k8v.resource_types.ResourceType.SECRETS)
        self.viewer.view()
        lines = self.viewer.config.file.getvalue().split("\n")
        assert len(lines) == 3
        m = re.search(
            r"secret/default/default-token-(.*) (\(.*\))",  # capture hash and extra data
            lines[0],
        )
        assert m != None
        assert m.group(0) == lines[0]
        assert m.group(2) == "(data=[ca.crt, namespace, token])"

        assert "secret/default/nginx-sec (data=[PASSWORD, USERNAME])" == lines[1]
        assert lines[2] == ""
