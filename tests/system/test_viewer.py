import pytest
import io
import re

import k8v


class TestViewer:
    def setup(self):
        self.viewer: Viewer = k8v.viewer.Viewer(k8v.config.Config())
        self.viewer.config.colors = None  # disable colors for now
        self.viewer.config.file = io.StringIO("")  # store output in StringIO

    def test_default_options(self):
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
