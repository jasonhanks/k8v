import pytest
import io
import munch
import pickle

import k8v


class TestBriefFormatter:
    """Validate the BriefPrinter output for each resource type."""

    def load_all(self, filename):
        with open(filename, "rb") as f:
            while True:
                try:
                    yield pickle.load(f)
                except EOFError:
                    break

    def load_and_display(self, filename, display=False):
        data = list(self.load_all(filename))
        if display:
            print()
            for num, r in enumerate(data):
                print(
                    f"#{num} {r.kind.lower()}/{r.metadata.namespace}/{r.metadata.name}"
                )
        return data

    def setup(self):
        self.config = k8v.config.Config(
            colors=None, file=io.StringIO(""), output="brief"
        )
        self.config.load()
        self.viewer = k8v.viewer.Viewer(self.config)

    def test_configmaps(self):
        """Validate our ConfigMaps format properly."""
        data = self.load_and_display("tests/fixtures/configmaps.pickle")
        self.viewer.print_resource(data[0], 0, 2, "")
        self.viewer.print_resource(data[1], 1, 2, "")
        assert (
            self.config.file.getvalue()
            == """configmap/default/kube-root-ca.crt
configmap/default/nginx-cm
"""
        )

    def test_configmaps_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_configmaps()  # should be the same

    def test_cronjobs(self):
        """Validate our CronJobs format properly."""
        data = self.load_and_display("tests/fixtures/cronjobs.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """cronjob/default/list-resources
"""
        )

    def test_cronjobs_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_cronjobs()  # should be the same

    def test_daemonsets(self):
        """Validate our CronJobs format properly."""
        data = self.load_and_display("tests/fixtures/daemonsets.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """daemonset/kube-system/kindnet
"""
        )

    def test_daemonsets_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        data = self.load_and_display("tests/fixtures/daemonsets.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """daemonset/kube-system/kindnet
        pod/kube-system/kindnet-v7dpv
"""
        )

    def test_deployments(self):
        """Validate our Deployments format properly."""
        data = self.load_and_display("tests/fixtures/deployments.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """deployment/default/nginx-deployment
"""
        )

    def test_deployments_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        data = self.load_and_display("tests/fixtures/deployments.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """deployment/default/nginx-deployment
        replicaset/default/nginx-deployment-7b6fcd488c
                pod/default/nginx-deployment-7b6fcd488c-sr2wv
                pod/default/nginx-deployment-7b6fcd488c-vrgrx
"""
        )

    def test_jobs(self):
        """Validate our Jobs format properly."""
        data = self.load_and_display("tests/fixtures/jobs.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """job/default/list-resources
"""
        )

    def test_jobs_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_jobs()  # should be the same

    def test_persistentvolume(self):
        """Validate our Jobs format properly."""
        data = self.load_and_display("tests/fixtures/persistentvolumes.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert "persistentvolume/pvc-" in self.config.file.getvalue()

    def test_persistentvolume_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_persistentvolume()  # should be the same

    def test_persistentvolumeclaim(self):
        """Validate our Jobs format properly."""
        data = self.load_and_display("tests/fixtures/persistentvolumeclaims.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """persistentvolumeclaim/default/nginx-pvc
"""
        )

    def test_persistentvolumeclaim_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_persistentvolumeclaim()  # should be the same

    def test_pods(self):
        """Validate our Jobs format properly."""
        data = self.load_and_display("tests/fixtures/pods.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """pod/default/list-resources-4rcts
"""
        )

    def test_pods_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_pods()  # should be the same

    def test_replicaset(self):
        """Validate our Jobs format properly."""
        data = self.load_and_display("tests/fixtures/replicasets.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """replicaset/default/nginx-deployment-7b6fcd488c
"""
        )

    def test_replicaset_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        data = self.load_and_display("tests/fixtures/replicasets.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """replicaset/default/nginx-deployment-7b6fcd488c
        pod/default/nginx-deployment-7b6fcd488c-sr2wv
        pod/default/nginx-deployment-7b6fcd488c-vrgrx
"""
        )

    def test_secrets(self):
        """Validate our Jobs format properly."""
        data = self.load_and_display("tests/fixtures/secrets.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """secret/default/default-token-5r2mb
"""
        )

    def test_secrets_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_secrets()  # should be the same

    def test_services(self):
        """Validate our Jobs format properly."""
        data = self.load_and_display("tests/fixtures/services.pickle")
        self.viewer.print_resource(data[0], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """service/default/kubernetes
"""
        )

    def test_services_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_secrets()  # should be the same
