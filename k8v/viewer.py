import k8v

# import k8v.config
# from k8v.resource_types import ResourceType
# import k8v.printer
# import k8v.searcher


class Viewer:
    """The Viewer is the main logic that will query the Kubernetes system and display the results."""

    def __init__(self, config: k8v.config.Config = k8v.config.Config()) -> None:
        self.config: config.Config = config
        self.printer: k8v.printer.Printer = k8v.printer.Printer(self)
        self.searcher: k8v.searcher.Searcher = k8v.searcher.Searcher(self)

    def view(self) -> None:
        """Use the input parameters to create a View of the desired resources and their relationships."""

        # show the input parameters
        if self.config.verbose:
            print(
                f"Display mode={self.config.output}, namespaces={self.config.namespaces}, resources={self.config.resources}, filters={self.config.includes}, selectors={self.config.selectors}"
            )

        # setup the API handlers
        self.printer.connect()
        self.searcher.connect()

        # setup default namespace if no overrides specified
        if self.config.namespaces is not None and len(self.config.namespaces) == 0:
            self.config.namespaces.append("default")

        # default resources to search
        if len(self.config.resources) == 0:
            self.config.resources = [
                k8v.resource_types.ResourceType.CONFIG_MAP,
                k8v.resource_types.ResourceType.SECRETS,
                k8v.resource_types.ResourceType.SERVICES,
                k8v.resource_types.ResourceType.INGRESS,
                k8v.resource_types.ResourceType.DAEMON_SETS,
                k8v.resource_types.ResourceType.DEPLOYMENTS,
                k8v.resource_types.ResourceType.PODS,
                k8v.resource_types.ResourceType.PERSISTENT_VOLUME,
                k8v.resource_types.ResourceType.PERSISTENT_VOLUME_CLAIM,
            ]

        # search for matching (and filtered) resources and print them out
        # using the desired display_mode.
        for type in self.config.resources:
            for resource in self.searcher.filter_resources(self.searcher.search(type)):
                self.printer.print(resource, type)
