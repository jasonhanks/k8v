import kubernetes
import collections
import json

from k8v.resource_types import ResourceType


class Searcher:
    def __init__(self, viewer):
        self.viewer = viewer
        self.config = viewer.config
        self._handlers = {}

    def setup(self):
        """Load the Kubernetes configuration and setup API endpoint connections."""
        self._handler_config = json.load(open("etc/handlers.json"))

        self.kubernetes_config = kubernetes.config.load_kube_config()
        self.api_client = kubernetes.client.ApiClient(self.kubernetes_config)

        for group, data in self._handler_config.items():
            if hasattr(kubernetes.client, group):
                self._handlers[group] = getattr(kubernetes.client, group)(
                    self.api_client
                )
            else:
                raise Exception(f"invalid resource handler{group}")

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
        for group, data in self._handler_config.items():
            if type.value[0] in data:
                # return the "all" or "namespace" specific handler as needed
                if self.config.namespaces is None:
                    return getattr(self._handlers[group], data[type.value[0]]["all"])
                elif data[type.value[0]].get("ns") and hasattr(
                    self._handlers[group], data[type.value[0]]["ns"]
                ):
                    return getattr(self._handlers[group], data[type.value[0]]["ns"])
                else:
                    return None
        return None

    def search_for_related(self, resource, type: ResourceType) -> list:
        """Search for any related resources of the given type."""

        if not self.config.related:
            return []

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
                    d.apiVersion = api_response.api_version
                    d.kind = api_response.kind.replace("List", "")
                    d._related = self.search_for_related(d, type)
                    resources.append(d)
            else:
                for ns in self.config.namespaces:
                    api_response = handler(ns, **kwargs)
                    for d in api_response.items:
                        d.type = type
                        d.apiVersion = api_response.api_version
                        d.kind = api_response.kind.replace("List", "")
                        d._related = self.search_for_related(d, type)
                        resources.append(d)
        except Exception as e:
            print(
                f"Exeception occurred while searching for resources ({type.value[0]}): {e}"
            )
            raise e

        # sort the resources by their names and return them
        return sorted(resources, key=lambda x: x.metadata.name)
