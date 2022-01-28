import k8v

from typing import NamedTuple


class Viewer:
    """The Viewer is the main logic that will query the Kubernetes system and display the results."""

    def __init__(self, config: k8v.config.Config = k8v.config.Config()) -> None:
        self.config: config.Config = config
        self.searcher: k8v.searcher.Searcher = k8v.searcher.Searcher(self)

    def setup(self) -> None:
        """Read configuration and prepare to begin processing results."""

        # setup the Printer to be used
        if self.config.output in ["brief", "b"]:
            self.printer: k8v.printer.Printer = k8v.printers.brief_printer.BriefPrinter(
                self
            )
        elif self.config.output in ["json", "j"]:
            self.printer: k8v.printer.Printer = k8v.printers.json_printer.JsonPrinter(
                self
            )
        else:
            self.printer: k8v.printer.Printer = (
                k8v.printers.default_printer.DefaultPrinter(self)
            )

        # start the Printer and Searcher
        self.printer.begin()
        self.searcher.begin()

        # setup default namespace if no overrides specified
        if self.config.namespaces is not None and len(self.config.namespaces) == 0:
            self.config.namespaces.append("default")

        # determine which resource types to search through
        if self.config.resources == None:
            self.config.resources = []
            for type in k8v.resource_types.ResourceType:
                self.config.resources.append(type)
        elif len(self.config.resources) == 0:
            self.config.resources = [
                k8v.resource_types.ResourceType.CONFIG_MAP,
                k8v.resource_types.ResourceType.SECRETS,
                k8v.resource_types.ResourceType.SERVICES,
                k8v.resource_types.ResourceType.INGRESS,
                k8v.resource_types.ResourceType.DAEMON_SETS,
                k8v.resource_types.ResourceType.STATEFUL_SETS,
                k8v.resource_types.ResourceType.REPLICA_SETS,
                k8v.resource_types.ResourceType.DEPLOYMENTS,
                k8v.resource_types.ResourceType.PODS,
                k8v.resource_types.ResourceType.PERSISTENT_VOLUME,
                k8v.resource_types.ResourceType.PERSISTENT_VOLUME_CLAIM,
            ]

    def view(self) -> None:
        """Use the input parameters to create a View of the desired resources and their relationships."""

        # show the input parameters
        if self.config.verbose:
            print(
                f"Display output={self.config.output}, namespaces={self.config.namespaces}, resources={self.config.resources}, filters={self.config.includes}, selectors={self.config.selectors}"
            )

        self.setup()

        # search for matching (and filtered) resources and print them out
        # using the desired display_mode.
        resources = []
        for type in self.config.resources:
            for resource in self.searcher.filter_resources(self.searcher.search(type)):
                resources.append(resource)

        for num, resource in enumerate(resources):
            self.printer.print(resource, delim="", index=num, total=len(resources) - 1)

        # stop the Printer and Searcher
        self.printer.end()
        self.searcher.end()
