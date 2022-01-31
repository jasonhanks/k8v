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

    def setup(self):
        self.data = list(self.load_all("tests/fixtures/test-data.pickle"))
        self.config = k8v.config.Config(
            colors=None, file=io.StringIO(""), output="brief"
        )
        self.config.load()
        self.viewer = k8v.viewer.Viewer(self.config)

    def test_display_pickle(self):
        """Display the pickle data and validate the entries have not changed."""
        print()
        for num, r in enumerate(self.data):
            print(f"#{num} {r.kind.lower()}/{r.metadata.namespace}/{r.metadata.name}")

    def test_configmaps(self):
        """Validate our ConfigMaps format properly."""
        self.viewer.print_resource(self.data[4], 0, 2, "")
        self.viewer.print_resource(self.data[12], 1, 2, "")
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
        self.viewer.print_resource(self.data[13], 0, 1, "")
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
        self.viewer.print_resource(self.data[16], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """daemonset/kube-system/kube-proxy
"""
        )

    def test_daemonsets_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.viewer.print_resource(self.data[16], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """daemonset/kube-system/kube-proxy
        pod/kube-system/kube-proxy-7pjmw
"""
        )

    def test_deployments(self):
        """Validate our Deployments format properly."""
        self.viewer.print_resource(self.data[25], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """deployment/default/nginx-deployment
"""
        )

    def test_deployments_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.viewer.print_resource(self.data[25], 0, 1, "")
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
        self.viewer.print_resource(self.data[29], 0, 1, "")
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
        self.viewer.print_resource(self.data[30], 0, 1, "")
        assert "persistentvolume/pvc-" in self.config.file.getvalue()

    def test_persistentvolume_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_persistentvolume()  # should be the same

    def test_persistentvolumeclaim(self):
        """Validate our Jobs format properly."""
        self.viewer.print_resource(self.data[31], 0, 1, "")
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
        self.viewer.print_resource(self.data[50], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """pod/default/nginx-deployment-7b6fcd488c-sr2wv
"""
        )

    def test_pods_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_pods()  # should be the same

    def test_replicaset(self):
        """Validate our Jobs format properly."""
        self.viewer.print_resource(self.data[49], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """replicaset/default/nginx-deployment-7b6fcd488c
"""
        )

    def test_replicaset_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.viewer.print_resource(self.data[49], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """replicaset/default/nginx-deployment-7b6fcd488c
        pod/default/nginx-deployment-7b6fcd488c-sr2wv
        pod/default/nginx-deployment-7b6fcd488c-vrgrx
"""
        )

    def test_secrets(self):
        """Validate our Jobs format properly."""
        self.viewer.print_resource(self.data[78], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """secret/default/nginx-sec
"""
        )

    def test_secrets_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_secrets()  # should be the same

    def test_services(self):
        """Validate our Jobs format properly."""
        self.viewer.print_resource(self.data[78], 0, 1, "")
        assert (
            self.config.file.getvalue()
            == """secret/default/nginx-sec
"""
        )

    def test_services_related(self):
        """Validate our ConfigMaps with related resources format properly."""
        self.config.related = True
        self.test_secrets()  # should be the same
