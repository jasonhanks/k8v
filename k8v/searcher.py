import kubernetes
import collections
import json

from k8v.resource_types import ResourceType


class Searcher:
    def __init__(self, viewer):
        self.viewer = viewer
        self.config = viewer.config

    def begin(self):
        """Load the Kubernetes configuration and setup API endpoint connections."""
        self.handlers = json.load(open("etc/handlers.json"))

        self.kubernetes_config = kubernetes.config.load_kube_config()
        self.api_client = kubernetes.client.ApiClient(self.kubernetes_config)
        self.api_core_v1 = kubernetes.client.CoreV1Api()
        self.api_apps_v1 = kubernetes.client.AppsV1Api(self.api_client)
        self.api_network_v1 = kubernetes.client.NetworkingV1Api()

    def end(self):
        """Stop the Searcher and cleanup anything if needed."""
        pass

    def filter_resources(self, resources):
        """Apply filtering logic to the specified resources."""

        # fitler by "includes" first
        for include in self.config.includes:
            resources = filter(lambda x: include in x.metadata.name, resources)

        # filter by label "selectors" next
        for label, value in self.config.selectors.items():
            resources = filter(
                lambda x: x.metadata.labels is not None
                and label in x.metadata.labels
                and x.metadata.labels[label] == value,
                resources,
            )

        # exclude anything undesirable lastly
        for exclude in self.config.excludes:
            resources = filter(lambda x: exclude not in x.metadata.name, resources)
        return resources

    def get_api_handler(self, type: ResourceType) -> str:
        """Retrieve the API handler function to use for the specified namespace(s) and ResourceType."""

        # do we understand this resource type?
        data = self.handlers.get(type.value[0])
        if data is None:
            return None

        # do we have a proper source for the handler?
        src = vars(self)[data["src"]]
        if src is None:
            return None

        # return the "all" or "namespace" specific handler as needed
        return (
            getattr(src, data["all"])
            if self.config.namespaces is None
            else getattr(src, data["ns"])
        )

    def get_pod_data(self, resource) -> [list, list]:
        """Get any related configmap or secrets related to this resource."""

        # search for "envFrom" sections in the container definitions
        data: dict = {"configmaps": [], "secrets": [], "pvcs": [], "volumes": []}
        if hasattr(resource, "spec") and hasattr(resource.spec, "containers"):
            for container in resource.spec.containers:
                if hasattr(container, "env_from") and container.env_from is not None:
                    for envFrom in container.env_from:
                        if (
                            hasattr(envFrom, "config_map_ref")
                            and envFrom.config_map_ref is not None
                        ):
                            data["configmaps"].append(envFrom.config_map_ref.name)
                        if (
                            hasattr(envFrom, "secret_ref")
                            and envFrom.secret_ref is not None
                        ):
                            data["secrets"].append(envFrom.secret_ref.name)

        # search through "volume" definitions
        if hasattr(resource, "spec") and hasattr(resource.spec, "volumes"):
            for volume in resource.spec.volumes:
                data["volumes"].append(volume)
                if volume.config_map is not None:
                    data["configmaps"].append(volume.config_map.name)
                elif volume.secret is not None:
                    data["secrets"].append(volume.secret.secret_name)
                elif volume.persistent_volume_claim is not None:
                    data["pvcs"].append(volume.persistent_volume_claim.claim_name)
        return data

    def search_for_related(self, resource, type: ResourceType) -> list:
        """Search for any related resources of the given type."""
        resources: list = []
        label_expr: str = ""

        if hasattr(resource, "spec") and hasattr(resource.spec, "selector"):
            selector = resource.spec.selector
            if (
                hasattr(selector, "match_expressions")
                and selector.match_expressions is not None
                and len(selector.match_expressions) > 0
            ):
                pass  # ignore since we cannot easily evaluate right now
            if hasattr(selector, "match_labels"):
                label_count: int = len(selector.match_labels) - 1
                for num, label in enumerate(selector.match_labels.items()):
                    label_expr += label[0] + "=" + label[1]
                    if num < label_count:
                        label_expr += ","
        elif resource.metadata.labels is not None and len(resource.metadata.labels) > 0:
            for num, label in enumerate(resource.metadata.labels):
                label_expr += label + "=" + resource.metadata.labels[label]
                if num < len(resource.metadata.labels) - 1:
                    label_expr += ","

        if type == ResourceType.DEPLOYMENTS:
            resources = self.search(
                ResourceType.REPLICA_SETS, label_selector=label_expr
            )
        elif type == ResourceType.DAEMON_SETS:
            resources = self.search(ResourceType.PODS, label_selector=label_expr)
        elif type == ResourceType.REPLICA_SETS:
            resources = self.search(ResourceType.PODS, label_selector=label_expr)
        elif type == ResourceType.STATEFUL_SETS:
            resources = filter(
                lambda x: resource.metadata.name in x.metadata.name,
                self.search(ResourceType.PODS),
            )
        return resources

    def search(self, type: ResourceType, **kwargs) -> list:
        """Search for matching resources for the specified type."""
        resources = []

        # deterine which API handler to use
        handler = self.get_api_handler(type)
        if handler is None:
            return resources

        try:
            if self.config.verbose:
                print(f"Searching for {type.value[0]}")

            if self.config.namespaces is None:
                api_response = handler(**kwargs)
                for d in api_response.items:
                    d.type = type
                    resources.append(d)
            else:
                for ns in self.config.namespaces:
                    api_response = handler(ns, **kwargs)
                    for d in api_response.items:
                        d.type = type
                        resources.append(d)
        except Exception as e:
            print(
                f"Exeception occurred while searching for resources ({type.value[0]}): {e}"
            )
            raise e

        # sort the resources by their names and return them
        return sorted(resources, key=lambda x: x.metadata.name)
