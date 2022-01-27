from io import StringIO

from k8v.printers.printer import PrinterBase


class BriefPrinter(PrinterBase):
    """The Printer that is used for the *brief* output type."""

    def print(self, resource, **kwargs) -> None:
        """Print out a resources and its information along with related resources."""
        type_text = self.get_api_type(resource.__class__.__name__)
        message = StringIO("")
        message.write(kwargs["delim"])
        message.write(self.get_text("type", type_text))
        message.write("/")
        if resource.metadata.namespace:
            message.write(self.get_text("namespace", resource.metadata.namespace))
            message.write("/")
        message.write(self.get_text("name", resource.metadata.name))

        if kwargs.get("out") is not None:
            kwargs["out"].write(message.getvalue())
        else:
            print(message.getvalue())

        # Ignore related resources unless they are needed
        if not self.config.related:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            self.print(related, **kwargs)
