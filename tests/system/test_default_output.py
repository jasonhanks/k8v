import pytest
import io
import json
import re

import k8v


class TestDefaultOutput:
    """These tests will run against a live Kubernetes cluster and validate the default resources displayed."""

    def setup(self):
        self.viewer: Viewer = k8v.viewer.Viewer(k8v.config.Config())
        self.viewer.config.colors = None  # disable colors for now
        self.viewer.config.file = io.StringIO("")  # store output in StringIO

    def test_brief_output(self):
        """Validate the *brief* output for the default resources."""
        self.viewer.config.output = "brief"
        self.viewer.view()
        lines = self.viewer.config.file.getvalue().split("\n")
        assert len(lines) == 11
        assert "configmap/default/kube-root-ca.crt" == lines[0]
        assert "configmap/default/nginx-cm" == lines[1]
        assert "secret/default/default-token-" in lines[2]
        assert "secret/default/nginx-sec" == lines[3]
        assert "service/default/kubernetes" == lines[4]
        assert "replicaset/default/nginx-deployment-" in lines[5]
        assert "deployment/default/nginx-deployment" == lines[6]
        assert "pod/default/nginx-deployment-" in lines[7]
        assert "pod/default/nginx-deployment-" in lines[8]
        assert "persistentvolumeclaim/default/nginx-pvc" == lines[9]

    def test_default_output(self):
        """Validate the *default* output for the default resources."""
        self.viewer.view()
        lines = self.viewer.config.file.getvalue().split("\n")
        assert len(lines) == 11
        assert lines[0] == "configmap/default/kube-root-ca.crt (data=[ca.crt])"
        assert lines[1] == "configmap/default/nginx-cm (data=[ENV, app])"

        m = re.search(
            r"secret/default/default-token-(.*) (\(.*\))",  # capture hash and extra data
            lines[2],
        )
        assert m != None
        assert m.group(0) == lines[2]
        assert m.group(2) == "(data=[ca.crt, namespace, token])"

        assert lines[3] == "secret/default/nginx-sec (data=[PASSWORD, USERNAME])"

        # verify service with a regex to grab the cluster IP
        m = re.search(
            r"service/default/kubernetes \(labels=\[component=apiserver provider=kubernetes\] type=ClusterIP cluster_ip=(.*) ports=\[443=6443/TCP \]\)",
            lines[4],
        )
        assert m != None
        assert m.group(0) == lines[4]
        assert m.group(1) is not None

        # verify replicaset
        m = re.search(
            r"replicaset/default/nginx-deployment-(.*) \(labels=\[app=nginx pod-template-hash=(.*)\] replicas=2/2 avail=2 generation=1\)",
            lines[5],
        )
        assert m != None
        assert m.group(0) == lines[5]
        assert m.group(1) is not None
        pod_hash = m.group(2)
        assert pod_hash is not None

        assert (
            lines[6]
            == "deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)"
        )

        # verify pods use the proper hash from the replicaset
        m = re.search(
            r"pod/default/nginx-deployment-(.*) \(labels=\[app=nginx pod-template-hash=(.*)\] sa=default configmaps=\[\['nginx-cm'\]\] pvcs=\[\['nginx-pvc'\]\]\)",
            lines[7],
        )
        assert m != None
        assert m.group(0) == lines[7]
        assert pod_hash in m.group(1)
        assert pod_hash == m.group(2)

        m = re.search(
            r"pod/default/nginx-deployment-(.*) \(labels=\[app=nginx pod-template-hash=(.*)\] sa=default configmaps=\[\['nginx-cm'\]\] pvcs=\[\['nginx-pvc'\]\]\)",
            lines[8],
        )
        assert m != None
        assert m.group(0) == lines[8]
        assert pod_hash in m.group(1)
        assert pod_hash == m.group(2)

        m = re.search(
            r"persistentvolumeclaim/default/nginx-pvc \(access_modes=standard storage_class=\['ReadWriteOnce'\] capacity=32Mi volume=(.*) phase=Bound\)",
            lines[9],
        )
        assert m != None
        assert m.group(0) == lines[9]
        assert m.group(1) is not None

        assert lines[10] == ""

    def test_json_output(self):
        """Validate the *JSON* output for the default resources."""
        self.viewer.config.output = "json"
        self.viewer.view()

        # make sure the JSON created is valid and can be parsed
        data = json.loads(self.viewer.config.file.getvalue())

        # validate some of the records to make sure it's working properly
        assert len(data) == 10

        assert "ConfigMap" == data[0]["kind"]
        assert "kube-root-ca.crt" == data[0]["metadata"]["name"]

        assert "ConfigMap" == data[1]["kind"]
        assert "nginx-cm" == data[1]["metadata"]["name"]
        assert "test" == data[1]["data"]["ENV"]
        assert "nginx" == data[1]["data"]["app"]

        assert "Secret" == data[2]["kind"]
        assert "default-token" in data[2]["metadata"]["name"]

        assert "Secret" == data[3]["kind"]
        assert "nginx-sec" in data[3]["metadata"]["name"]

        assert "Service" == data[4]["kind"]
        assert "kubernetes" in data[4]["metadata"]["name"]
        assert "ClusterIP" == data[4]["spec"]["type"]
        assert 443 == data[4]["spec"]["ports"][0]["port"]
        assert 6443 == data[4]["spec"]["ports"][0]["target_port"]

        assert "ReplicaSet" == data[5]["kind"]
        assert "nginx-deployment" in data[5]["metadata"]["name"]
        assert 2 == data[5]["spec"]["replicas"]

        assert "Deployment" == data[6]["kind"]
        assert "nginx-deployment" == data[6]["metadata"]["name"]
        assert 2 == data[6]["spec"]["replicas"]

        assert "Pod" == data[7]["kind"]
        assert "nginx-deployment-" in data[7]["metadata"]["name"]
        assert "nginx:alpine" == data[7]["spec"]["containers"][0]["image"]
        assert "Pod" == data[8]["kind"]
        assert "nginx-deployment-" in data[8]["metadata"]["name"]
        assert "nginx" == data[7]["spec"]["containers"][0]["name"]

        assert "PersistentVolumeClaim" == data[9]["kind"]
        assert "nginx-pvc" == data[9]["metadata"]["name"]
