from io import StringIO

from k8v.printers.printer import PrinterBase


class BriefPrinter(PrinterBase):
    """The Printer that is used for the *brief* output type."""

    def print(self, resource, **kwargs) -> None:
        """Print out a resources and its information along with related resources."""
        message = StringIO("")
        message.write(kwargs["delim"])
        message.write(self.get_text("type", resource.type.value[0]))
        message.write("/")
        if hasattr(resource.metadata, "namespace") and resource.metadata.namespace:
            message.write(self.get_text("namespace", resource.metadata.namespace))
            message.write("/")
        message.write(self.get_text("name", resource.metadata.name))

        self.viewer.config.file.write(message.getvalue() + "\n")

        # Ignore related resources unless they are needed
        if not self.config.related:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            self.print(related, **kwargs)
