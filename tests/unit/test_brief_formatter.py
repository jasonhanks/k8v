import pytest
import io
import munch

import k8v

from test_base import TestBase


class TestBriefFormatter(TestBase):
    """Validate the BriefFormatter output for each resource type."""

    def setup(self):
        self.config = k8v.config.Config(
            colors=None, file=io.StringIO(""), output="brief"
        )
        self.config.load()
        self.printer = k8v.printer.Printer(self.config)

    def test_configmaps(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/configmaps.pickle"))
        assert (
            self.config.file.getvalue()
            == """configmap/default/kube-root-ca.crt
configmap/default/nginx-cm
"""
        )

    def test_configmaps_related(self):
        self.config.related = True
        self.test_configmaps()  # should be the same

    def test_cronjobs(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/cronjobs.pickle"))
        assert (
            self.config.file.getvalue()
            == """cronjob/default/list-resources
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
            == """daemonset/kube-system/kindnet
daemonset/kube-system/kube-proxy
"""
        )

    def test_daemonsets_related(self):
        self.config.related = True
        self.printer.print_all(self.load_fixture("tests/fixtures/daemonsets.pickle"))
        assert (
            self.config.file.getvalue()
            == """daemonset/kube-system/kindnet
        pod/kube-system/kindnet-v7dpv
pod/kube-system/kindnet-v7dpv
daemonset/kube-system/kube-proxy
        pod/kube-system/kube-proxy-7pjmw
pod/kube-system/kube-proxy-7pjmw
"""
        )

    def test_deployments(self):
        self.printer.print_all(
            [self.load_fixture("tests/fixtures/deployments.pickle")[0]]
        )
        assert (
            self.config.file.getvalue()
            == """deployment/default/nginx-deployment
"""
        )

    def test_deployments_related(self):
        self.config.related = True
        self.printer.print_all(
            [self.load_fixture("tests/fixtures/deployments.pickle")[0]]
        )
        assert (
            self.config.file.getvalue()
            == """deployment/default/nginx-deployment
        replicaset/default/nginx-deployment-7b6fcd488c
                pod/default/nginx-deployment-7b6fcd488c-sr2wv
                pod/default/nginx-deployment-7b6fcd488c-vrgrx
"""
        )

    def test_jobs(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/jobs.pickle"))
        assert (
            self.config.file.getvalue()
            == """job/default/list-resources
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
            == """persistentvolumeclaim/default/nginx-pvc
"""
        )

    def test_persistentvolumeclaim_related(self):
        self.config.related = True
        self.test_persistentvolumeclaim()  # should be the same

    def test_pods(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/pods.pickle"))
        assert (
            self.config.file.getvalue()
            == """pod/default/list-resources-4rcts
pod/default/nginx-deployment-7b6fcd488c-sr2wv
pod/default/nginx-deployment-7b6fcd488c-vrgrx
"""
        )

    def test_pods_related(self):
        self.config.related = True
        self.test_pods()  # should be the same

    def test_replicaset(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/replicasets.pickle"))

        assert (
            self.config.file.getvalue()
            == """replicaset/default/nginx-deployment-7b6fcd488c
pod/default/nginx-deployment-7b6fcd488c-sr2wv
pod/default/nginx-deployment-7b6fcd488c-vrgrx
"""
        )

    def test_replicaset_related(self):
        self.config.related = True
        self.printer.print_all(self.load_fixture("tests/fixtures/replicasets.pickle"))
        assert (
            self.config.file.getvalue()
            == """replicaset/default/nginx-deployment-7b6fcd488c
        pod/default/nginx-deployment-7b6fcd488c-sr2wv
        pod/default/nginx-deployment-7b6fcd488c-vrgrx
pod/default/nginx-deployment-7b6fcd488c-sr2wv
pod/default/nginx-deployment-7b6fcd488c-vrgrx
"""
        )

    def test_secrets(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/secrets.pickle"))
        assert (
            self.config.file.getvalue()
            == """secret/default/default-token-5r2mb
secret/default/nginx-sec
"""
        )

    def test_secrets_related(self):
        self.config.related = True
        self.test_secrets()  # should be the same

    def test_services(self):
        self.printer.print_all(self.load_fixture("tests/fixtures/services.pickle"))
        assert (
            self.config.file.getvalue()
            == """service/default/kubernetes
service/default/nginx
"""
        )

    def test_services_related(self):
        self.config.related = True
        self.test_secrets()  # should be the same
