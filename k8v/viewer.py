import config
from resource_types import ResourceType
import printer
import searcher


class Viewer:
    """The Viewer is the main logic that will query the Kubernetes system and display the results."""

    def __init__(self, config: config.Config = config.Config(), delim: str = "        ") -> None:
        self.config: config.Config = config
        self.delim: str = delim

        self.printer: printer.Printer = printer.Printer(self)
        self.searcher: searcher.Searcher = searcher.Searcher(self)


    def view(self) -> None:
        """Use the input parameters to create a View of the desired resources and their relationships."""

        # show the input parameters
        if self.config.verbose:
            print(f"Display mode={self.config.display_type}, namespaces={self.config.namespaces}, resources={self.config.resources}, filters={self.config.includes}, selectors={self.config.selectors}")

        # setup the API handlers
        self.printer.connect()
        self.searcher.connect()

        # setup default namespace if no overrides specified
        if self.config.namespaces is not None and len(self.config.namespaces) == 0:
            self.config.namespaces.append("default")

        # default resources to search
        if len(self.config.resources) == 0:
            self.config.resources = [
                ResourceType.CONFIG_MAP,
                ResourceType.SECRETS,
                ResourceType.SERVICES,
                ResourceType.INGRESS,
                ResourceType.DAEMON_SETS,
                ResourceType.DEPLOYMENTS,
                ResourceType.PODS,
                ResourceType.PERSISTENT_VOLUME,
                ResourceType.PERSISTENT_VOLUME_CLAIM,
            ]

        # search for matching (and filtered) resources and print them out
        # using the desired display_mode.
        for type in self.config.resources:
            resources = self.searcher.search(type)
            for resource in self.searcher.filter_resources(resources):
                self.printer.print(resource, type)
