from k8v.printers.printer import PrinterBase


class BriefPrinter(PrinterBase):
    """The Printer that is used for the *brief* output type."""

    def print(self, resource, **kwargs) -> None:
        """Print out a resources and its information along with related resources."""
        message = kwargs["delim"] + self.get_ansi_text(
            "type", self.get_api_type(resource.__class__.__name__)
        )
        message += "/"
        message += f"{self.get_ansi_text('namespace', resource.metadata.namespace) +'/' if resource.metadata.namespace else ''}"
        message += self.get_ansi_text("name", resource.metadata.name)
        print(message)

        # Ignore related resources unless they are needed
        if self.config.related == False:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            self.print(related, **kwargs)
