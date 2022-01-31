import k8v


class Printer:
    """The Printer is responsible for using the Formatters to generate the output properly."""

    def __init__(self, config: k8v.config.Config):
        self.config = config

    def print(self, resource, num=1, max=1, delim=""):
        self.config.formatter.begin_resource()
        self.config.formatter.print(resource, delim)
        self.config.formatter.end_resource(num == max)

        if self.config.related and len(resource._related) > 0:
            for n, r in enumerate(resource._related):
                self.print(r, n, len(resource._related), delim + self.config.delimeter)

    def print_all(self, resources):
        """Properly format a list of resources found by the tool."""

        # Print any beginning formatting needed (ex: JSON needs [ to denote the List)
        self.config.formatter.begin()

        # Format each resource and print() it to the output file
        for num, resource in enumerate(resources):
            self.print(resource, num, len(resources) - 1, "")

        # Print any closing formatting needed (ex: JSON needs ] to close the List)
        self.config.formatter.end()
