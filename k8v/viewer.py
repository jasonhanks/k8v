import k8v


class Viewer:
    """The Viewer is the main logic that will query the Kubernetes system and display the results."""

    def __init__(self, config: k8v.config.Config = k8v.config.Config()) -> None:
        self.config: config.Config = config
        self.printer: k8v.printer.Printer = k8v.printer.Printer(self.config)
        self.searcher: k8v.searcher.Searcher = k8v.searcher.Searcher(self)

    def view(self) -> None:
        """Use the input parameters to create a View of the desired resources and their relationships."""

        # show the input parameters
        if self.config.verbose:
            print(
                f"Display output={self.config.output}, namespaces={self.config.namespaces}, resources={self.config.resources}, filters={self.config.includes}, selectors={self.config.selectors}"
            )

        # Load configuration files
        self.config.load()
        self.searcher.setup()

        # search for matching (and filtered) resources
        resources = []
        for type in self.config.resources:
            for r in self.searcher.filter_resources(self.searcher.search(type)):
                resources.append(r)

        # use the Printer to print the results out as a group
        self.printer.print_all(resources)
