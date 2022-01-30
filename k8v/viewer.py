import k8v


class Viewer:
    """The Viewer is the main logic that will query the Kubernetes system and display the results."""

    def __init__(self, config: k8v.config.Config = k8v.config.Config()) -> None:
        self.config: config.Config = config
        self.searcher: k8v.searcher.Searcher = k8v.searcher.Searcher(self)

    def print_resource(self, resource, num=1, max=1, delim=""):
        self.config.formatter.begin_resource()
        self.config.formatter.print(resource, delim)
        self.config.formatter.end_resource(num == max)

        if self.config.related and len(resource._related) > 0:
            for n, r in enumerate(resource._related):
                self.print_resource(
                    r, n, len(resource._related), delim + self.config.delimeter
                )

    def view(self) -> None:
        """Use the input parameters to create a View of the desired resources and their relationships."""

        # show the input parameters
        if self.config.verbose:
            print(
                f"Display output={self.config.output}, namespaces={self.config.namespaces}, resources={self.config.resources}, filters={self.config.includes}, selectors={self.config.selectors}"
            )

        # Load configuration files
        self.config.load()
        self.searcher.begin()

        # search for matching (and filtered) resources
        resources = []
        self.config.formatter.begin()
        for type in self.config.resources:
            for r in self.searcher.filter_resources(self.searcher.search(type)):
                resources.append(r)

        for num, resource in enumerate(resources):
            self.print_resource(resource, num, len(resources) - 1, "")
        self.config.formatter.end()

        self.searcher.end()
