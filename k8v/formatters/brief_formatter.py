import io

from k8v.formatters.formatter import FormatterBase


class BriefFormatter(FormatterBase):
    """The Printer that is used for the *brief* output type."""

    def print(self, resource, delim: str) -> None:
        """Print out a resources and its information along with related resources."""
        message = io.StringIO("")
        message.write(delim)
        message.write(self.get_text("type", resource.type.value[0]))
        message.write("/")
        if hasattr(resource.metadata, "namespace") and resource.metadata.namespace:
            message.write(self.get_text("namespace", resource.metadata.namespace))
            message.write("/")
        message.write(self.get_text("name", resource.metadata.name))

        self.config.file.write(message.getvalue())
