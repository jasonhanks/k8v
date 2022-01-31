import pytest
import io
import json
import munch

import k8v

from test_base import TestBase


class TestDefaultFormatter(TestBase):
    """Validate the DefaultFormatter output for each resource type."""

    def setup(self):
        self.config = k8v.config.Config(colors=None, file=io.StringIO(""))
        self.config.load()
        self.printer = k8v.printer.Printer(self.config)

    def test_configmaps(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/configmaps.pickle"))
        assert (
            self.config.file.getvalue()
            == """configmap/default/kube-root-ca.crt (data=[ca.crt])
configmap/default/nginx-cm (data=[ENV, app])
"""
        )

    def test_configmaps_related(self):
        self.config.related = True
        self.test_configmaps()  # should be the same

    def test_cronjobs(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/cronjobs.pickle"))
        assert (
            self.config.file.getvalue()
            == """cronjob/default/list-resources ()
"""
        )

    def test_cronjobs_related(self):
        self.config.related = True
        self.test_cronjobs()  # should be the same

    def test_daemonsets(self):
        data = self.load_fixture("tests/fixtures/daemonsets.pickle")
        self.printer.print_all([data[0], data[2]])
        assert (
            self.config.file.getvalue()
            == """daemonset/kube-system/kindnet (labels=[app=kindnet k8s-app=kindnet tier=node] )
daemonset/kube-system/kube-proxy (labels=[k8s-app=kube-proxy] )
"""
        )

    def test_daemonsets_related(self):
        self.config.related = True
        self.printer.print_all(self.load_fixture("tests/fixtures/daemonsets.pickle"))
        assert (
            self.config.file.getvalue()
            == """daemonset/kube-system/kindnet (labels=[app=kindnet k8s-app=kindnet tier=node] )
        pod/kube-system/kindnet-v7dpv (labels=[app=kindnet controller-revision-hash=5b547684d9 k8s-app=kindnet pod-template-generation=1 tier=node] sa=kindnet )
pod/kube-system/kindnet-v7dpv (labels=[app=kindnet controller-revision-hash=5b547684d9 k8s-app=kindnet pod-template-generation=1 tier=node] sa=kindnet )
daemonset/kube-system/kube-proxy (labels=[k8s-app=kube-proxy] )
        pod/kube-system/kube-proxy-7pjmw (labels=[controller-revision-hash=6bc6858f58 k8s-app=kube-proxy pod-template-generation=1] sa=kube-proxy configmaps=[['kube-proxy']])
pod/kube-system/kube-proxy-7pjmw (labels=[controller-revision-hash=6bc6858f58 k8s-app=kube-proxy pod-template-generation=1] sa=kube-proxy configmaps=[['kube-proxy']])
"""
        )

    def test_deployments(self):
        self.printer.print_all(
            [self.load_fixture("tests/fixtures/deployments.pickle")[0]]
        )
        assert (
            self.config.file.getvalue()
            == """deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)
"""
        )

    def test_deployments_related(self):
        self.config.related = True
        self.printer.print_all(
            [self.load_fixture("tests/fixtures/deployments.pickle")[0]]
        )
        assert (
            self.config.file.getvalue()
            == """deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)
        replicaset/default/nginx-deployment-7b6fcd488c (labels=[app=nginx pod-template-hash=7b6fcd488c] replicas=2/2 avail=2 generation=1)
                pod/default/nginx-deployment-7b6fcd488c-sr2wv (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
                pod/default/nginx-deployment-7b6fcd488c-vrgrx (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
"""
        )

    def test_jobs(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/jobs.pickle"))
        assert (
            self.config.file.getvalue()
            == """job/default/list-resources (labels=[controller-uid=bcc11bfb-8c46-4878-b24f-41d025d028f8 job-name=list-resources] )
"""
        )

    def test_jobs_related(self):
        self.config.related = True
        self.test_jobs()  # should be the same

    def test_persistentvolume(self):
        self.printer.print_all(
            self.load_fixture("tests/fixtures/persistentvolumes.pickle")
        )
        assert "persistentvolume/pvc-" in self.config.file.getvalue()

    def test_persistentvolume_related(self):
        self.config.related = True
        self.test_persistentvolume()  # should be the same

    def test_persistentvolumeclaim(self):
        self.printer.print_all(
            self.load_fixture("tests/fixtures/persistentvolumeclaims.pickle")
        )
        assert (
            self.config.file.getvalue()
            == """persistentvolumeclaim/default/nginx-pvc (access_modes=standard storage_class=['ReadWriteOnce'] capacity=32Mi volume=pvc-01fa476c-970e-4e16-a547-2afa6854257d phase=Bound)
"""
        )

    def test_persistentvolumeclaim_related(self):
        self.config.related = True
        self.test_persistentvolumeclaim()  # should be the same

    def test_pods(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/pods.pickle"))
        assert (
            self.config.file.getvalue()
            == """pod/default/list-resources-4rcts (labels=[controller-uid=bcc11bfb-8c46-4878-b24f-41d025d028f8 job-name=list-resources] sa=default )
pod/default/nginx-deployment-7b6fcd488c-sr2wv (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
pod/default/nginx-deployment-7b6fcd488c-vrgrx (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
"""
        )

    def test_pods_related(self):
        self.config.related = True
        self.test_pods()  # should be the same

    def test_replicaset(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/replicasets.pickle"))
        assert (
            self.config.file.getvalue()
            == """replicaset/default/nginx-deployment-7b6fcd488c (labels=[app=nginx pod-template-hash=7b6fcd488c] replicas=2/2 avail=2 generation=1)
pod/default/nginx-deployment-7b6fcd488c-sr2wv (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
pod/default/nginx-deployment-7b6fcd488c-vrgrx (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
"""
        )

    def test_replicaset_related(self):
        self.config.related = True
        self.printer.print_all(self.load_fixture("tests/fixtures/replicasets.pickle"))
        assert (
            self.config.file.getvalue()
            == """replicaset/default/nginx-deployment-7b6fcd488c (labels=[app=nginx pod-template-hash=7b6fcd488c] replicas=2/2 avail=2 generation=1)
        pod/default/nginx-deployment-7b6fcd488c-sr2wv (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
        pod/default/nginx-deployment-7b6fcd488c-vrgrx (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
pod/default/nginx-deployment-7b6fcd488c-sr2wv (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
pod/default/nginx-deployment-7b6fcd488c-vrgrx (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
"""
        )

    def test_secrets(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/secrets.pickle"))
        assert (
            self.config.file.getvalue()
            == """secret/default/default-token-5r2mb (data=[ca.crt, namespace, token])
secret/default/nginx-sec (data=[PASSWORD, USERNAME])
"""
        )

    def test_secrets_related(self):
        self.config.related = True
        self.test_secrets()  # should be the same

    def test_services(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/services.pickle"))
        assert (
            self.config.file.getvalue()
            == """service/default/kubernetes (labels=[component=apiserver provider=kubernetes] type=ClusterIP cluster_ip=10.96.0.1 ports=[443=6443/TCP ])
service/default/nginx (type=ClusterIP cluster_ip=10.96.33.145 ports=[80=80/TCP ])
"""
        )

    def test_services_related(self):
        self.config.related = True
        self.test_secrets()  # should be the same
