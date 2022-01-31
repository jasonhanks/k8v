import pytest
import io
import json
import re

import k8v


class TestDefaultResourceOutput:
    """These tests will run against a live Kubernetes cluster and validate the default resources displayed."""

    def setup(self):
        self.viewer: Viewer = k8v.viewer.Viewer(
            k8v.config.Config(colors=None, file=io.StringIO(""))
        )

    def test_brief_output(self):
        """Validate the *brief* output for the default resources."""
        self.viewer.config.output = "brief"
        self.viewer.view()
        lines = self.viewer.config.file.getvalue().split("\n")
        assert len(lines) == 15
        assert "configmap/default/kube-root-ca.crt" == lines[0]
        assert "configmap/default/nginx-cm" == lines[1]
        assert "cronjob/default/list-resources" == lines[2]
        assert "deployment/default/nginx-deployment" == lines[3]
        assert "job/default/list-resources" == lines[4]
        assert "persistentvolumeclaim/default/nginx-pvc" == lines[5]
        assert "pod/default/list-resources-" in lines[6]
        assert "pod/default/nginx-deployment-" in lines[7]
        assert "pod/default/nginx-deployment-" in lines[8]
        assert "replicaset/default/nginx-deployment-" in lines[9]
        assert "secret/default/default-token-" in lines[10]
        assert "secret/default/nginx-sec" == lines[11]
        assert "service/default/kubernetes" == lines[12]

    def test_default_output(self):
        """Validate the *default* output for the default resources."""
        self.viewer.view()
        lines = self.viewer.config.file.getvalue().split("\n")
        assert len(lines) == 15
        assert lines[0] == "configmap/default/kube-root-ca.crt (data=[ca.crt])"
        assert lines[1] == "configmap/default/nginx-cm (data=[ENV, app])"
        assert lines[2] == "cronjob/default/list-resources ()"

        m = re.search(
            r"replicaset/default/nginx-deployment-(.*) \(labels=\[app=nginx pod-template-hash=(.*)\] replicas=2/2 avail=2 generation=1\)",
            lines[9],
        )
        assert m != None
        assert m.group(0) == lines[9]
        assert m.group(1) is not None
        pod_hash = m.group(2)
        assert pod_hash is not None

        assert (
            lines[3]
            == "deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)"
        )

        m = re.search(
            r"job/default/list-resources \(labels=\[controller-uid=(.*) job-name=list-resources\] \)",
            lines[4],
        )
        assert m != None
        assert m.group(0) == lines[4]
        assert m.group(1) is not None

        m = re.search(
            r"persistentvolumeclaim/default/nginx-pvc \(access_modes=standard storage_class=\['ReadWriteOnce'\] capacity=32Mi volume=(.*) phase=Bound\)",
            lines[5],
        )
        assert m != None
        assert m.group(0) == lines[5]
        assert m.group(1) is not None

        m = re.search(
            r"pod/default/list-resources-(.*) \(labels=\[controller-uid=(.*) job-name=list-resources\] sa=default \)",
            lines[6],
        )
        assert m != None
        assert m.group(0) == lines[6]
        assert m.group(1) is not None

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
            r"secret/default/default-token-(.*) (\(.*\))",  # capture hash and extra data
            lines[10],
        )
        assert m != None
        assert m.group(0) == lines[10]
        assert m.group(2) == "(data=[ca.crt, namespace, token])"

        assert lines[11] == "secret/default/nginx-sec (data=[PASSWORD, USERNAME])"

        # verify service with a regex to grab the cluster IP
        m = re.search(
            r"service/default/kubernetes \(labels=\[component=apiserver provider=kubernetes\] type=ClusterIP cluster_ip=(.*) ports=\[443=6443/TCP \]\)",
            lines[12],
        )
        assert m != None
        assert m.group(0) == lines[12]
        assert m.group(1) is not None

        assert (
            lines[13]
            == "service/default/nginx (type=ClusterIP cluster_ip=10.96.33.145 ports=[80=80/TCP ])"
        )
        assert lines[14] == ""

    def test_json_output(self):
        """Validate the *JSON* output for the default resources."""
        self.viewer.config.output = "json"
        self.viewer.view()

        # make sure the JSON created is valid and can be parsed
        data = json.loads(self.viewer.config.file.getvalue())

        # validate some of the records to make sure it's working properly
        assert len(data) == 14

        assert "ConfigMap" == data[0]["kind"]
        assert "kube-root-ca.crt" == data[0]["metadata"]["name"]

        assert "ConfigMap" == data[1]["kind"]
        assert "nginx-cm" == data[1]["metadata"]["name"]
        assert "test" == data[1]["data"]["ENV"]
        assert "nginx" == data[1]["data"]["app"]

        assert "CronJob" == data[2]["kind"]
        assert "list-resources" == data[2]["metadata"]["name"]

        assert "Deployment" == data[3]["kind"]
        assert "nginx-deployment" == data[3]["metadata"]["name"]
        assert 2 == data[3]["spec"]["replicas"]

        assert "Job" == data[4]["kind"]
        assert "list-resources" == data[4]["metadata"]["name"]

        assert "PersistentVolumeClaim" == data[5]["kind"]
        assert "nginx-pvc" == data[5]["metadata"]["name"]

        assert "Pod" == data[6]["kind"]
        assert "list-resources-" in data[6]["metadata"]["name"]
        assert "ubuntu:latest" == data[6]["spec"]["containers"][0]["image"]

        assert "Pod" == data[7]["kind"]
        assert "nginx-deployment-" in data[7]["metadata"]["name"]
        assert "nginx:alpine" == data[7]["spec"]["containers"][0]["image"]
        assert "Pod" == data[8]["kind"]
        assert "nginx-deployment-" in data[8]["metadata"]["name"]
        assert "nginx" == data[8]["spec"]["containers"][0]["name"]

        assert "ReplicaSet" == data[9]["kind"]
        assert "nginx-deployment" in data[9]["metadata"]["name"]
        assert 2 == data[9]["spec"]["replicas"]

        assert "Secret" == data[10]["kind"]
        assert "default-token" in data[10]["metadata"]["name"]

        assert "Secret" == data[11]["kind"]
        assert "nginx-sec" in data[11]["metadata"]["name"]

        assert "Service" == data[12]["kind"]
        assert "kubernetes" in data[12]["metadata"]["name"]
        assert "ClusterIP" == data[12]["spec"]["type"]
        assert 443 == data[12]["spec"]["ports"][0]["port"]
        assert 6443 == data[12]["spec"]["ports"][0]["target_port"]
