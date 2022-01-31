import pytest
import io
import json
import munch

import k8v

from base_test import BaseTest


class TestJsonFormatter(BaseTest):
    """Validate the JsonFormatter output for each resource type."""

    def setup(self):
        self.config = k8v.config.Config(
            colors=None, file=io.StringIO(""), output="json"
        )
        self.config.load()
        self.printer = k8v.printer.Printer(self.config)

    def test_configmaps(self):
        data = self.load_and_display("tests/fixtures/configmaps.pickle")
        self.printer.print_all(data)

        # convert the output from JSON to a munchified object
        obj = munch.munchify(json.loads(self.config.file.getvalue()))

        assert len(obj) == len(data)
        assert data[0].metadata.name == obj[0].metadata.name
        assert obj[0].metadata.name == "kube-root-ca.crt"
        assert obj[1].metadata.name == "nginx-cm"
        assert obj[1].data.toDict() == {"ENV": "test", "app": "nginx"}

    def test_configmaps_related(self):
        self.config.related = True
        self.test_configmaps()  # should be the same

    def test_cronjobs(self):
        data = self.load_and_display("tests/fixtures/cronjobs.pickle")
        self.printer.print_all(data)

        # convert the output from JSON to a munchified object
        obj = munch.munchify(json.loads(self.config.file.getvalue()))

        assert len(obj) == len(data)
        assert data[0].metadata.name == obj[0].metadata.name
        assert obj[0].metadata.name == "list-resources"
        assert obj[0].spec.suspend == True
        assert obj[0].spec.schedule == "0 0 * * *"
        assert obj[0].spec.job_template.spec.ttl_seconds_after_finished == 10
        assert obj[0].spec.job_template.spec.backoff_limit == 1
        assert obj[0].spec.job_template.spec.active_deadline_seconds == 60
        assert obj[0].spec.job_template.spec.template.spec.restart_policy == "Never"
        assert (
            obj[0].spec.job_template.spec.template.spec.containers[0].name
            == "list-resources"
        )

    def test_cronjobs_related(self):
        self.config.related = True
        self.test_cronjobs()  # should be the same


#     def test_daemonsets(self):
#         data = self.load_and_display("tests/fixtures/daemonsets.pickle")
#         self.viewer.print_resource(data[0], 1, 2, "")
#         self.viewer.print_resource(data[2], 2, 2, "")
#         assert (
#             self.config.file.getvalue()
#             == """daemonset/kube-system/kindnet
# daemonset/kube-system/kube-proxy
# """
#         )

#     def test_daemonsets_related(self):
#         self.config.related = True
#         data = self.load_and_display("tests/fixtures/daemonsets.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert (
#             self.config.file.getvalue()
#             == """daemonset/kube-system/kindnet
#         pod/kube-system/kindnet-v7dpv
# pod/kube-system/kindnet-v7dpv
# daemonset/kube-system/kube-proxy
#         pod/kube-system/kube-proxy-7pjmw
# pod/kube-system/kube-proxy-7pjmw
# """
#         )

#     def test_deployments(self):
#         data = self.load_and_display("tests/fixtures/deployments.pickle")
#         self.viewer.print_resource(data[0], 0, 1, "")
#         assert (
#             self.config.file.getvalue()
#             == """deployment/default/nginx-deployment
# """
#         )

#     def test_deployments_related(self):
#         self.config.related = True
#         data = self.load_and_display("tests/fixtures/deployments.pickle")
#         self.viewer.print_resource(data[0], 0, 1, "")
#         assert (
#             self.config.file.getvalue()
#             == """deployment/default/nginx-deployment
#         replicaset/default/nginx-deployment-7b6fcd488c
#                 pod/default/nginx-deployment-7b6fcd488c-sr2wv
#                 pod/default/nginx-deployment-7b6fcd488c-vrgrx
# """
#         )

#     def test_jobs(self):
#         data = self.load_and_display("tests/fixtures/jobs.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert (
#             self.config.file.getvalue()
#             == """job/default/list-resources
# """
#         )

#     def test_jobs_related(self):
#         self.config.related = True
#         self.test_jobs()  # should be the same

#     def test_persistentvolume(self):
#         data = self.load_and_display("tests/fixtures/persistentvolumes.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert "persistentvolume/pvc-" in self.config.file.getvalue()

#     def test_persistentvolume_related(self):
#         self.config.related = True
#         self.test_persistentvolume()  # should be the same

#     def test_persistentvolumeclaim(self):
#         data = self.load_and_display("tests/fixtures/persistentvolumeclaims.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert (
#             self.config.file.getvalue()
#             == """persistentvolumeclaim/default/nginx-pvc
# """
#         )

#     def test_persistentvolumeclaim_related(self):
#         self.config.related = True
#         self.test_persistentvolumeclaim()  # should be the same

#     def test_pods(self):
#         data = self.load_and_display("tests/fixtures/pods.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert (
#             self.config.file.getvalue()
#             == """pod/default/list-resources-4rcts
# pod/default/nginx-deployment-7b6fcd488c-sr2wv
# pod/default/nginx-deployment-7b6fcd488c-vrgrx
# """
#         )

#     def test_pods_related(self):
#         self.config.related = True
#         self.test_pods()  # should be the same

#     def test_replicaset(self):
#         data = self.load_and_display("tests/fixtures/replicasets.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert (
#             self.config.file.getvalue()
#             == """replicaset/default/nginx-deployment-7b6fcd488c
# pod/default/nginx-deployment-7b6fcd488c-sr2wv
# pod/default/nginx-deployment-7b6fcd488c-vrgrx
# """
#         )

#     def test_replicaset_related(self):
#         self.config.related = True
#         data = self.load_and_display("tests/fixtures/replicasets.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert (
#             self.config.file.getvalue()
#             == """replicaset/default/nginx-deployment-7b6fcd488c
#         pod/default/nginx-deployment-7b6fcd488c-sr2wv
#         pod/default/nginx-deployment-7b6fcd488c-vrgrx
# pod/default/nginx-deployment-7b6fcd488c-sr2wv
# pod/default/nginx-deployment-7b6fcd488c-vrgrx
# """
#         )

#     def test_secrets(self):
#         data = self.load_and_display("tests/fixtures/secrets.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert (
#             self.config.file.getvalue()
#             == """secret/default/default-token-5r2mb
# secret/default/nginx-sec
# """
#         )

#     def test_secrets_related(self):
#         self.config.related = True
#         self.test_secrets()  # should be the same

#     def test_services(self):
#         data = self.load_and_display("tests/fixtures/services.pickle")
#         for num, resource in enumerate(data):
#             self.viewer.print_resource(resource, num, len(data), "")
#         assert (
#             self.config.file.getvalue()
#             == """service/default/kubernetes
# service/default/nginx
# """
#         )

#     def test_services_related(self):
#         self.config.related = True
#         self.test_secrets()  # should be the same
