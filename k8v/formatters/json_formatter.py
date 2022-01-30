import jsons

from kubernetes.client.configuration import Configuration

from k8v.formatters.formatter import FormatterBase
from k8v.resource_types import ResourceType


class JsonFormatter(FormatterBase):
    """The Printer used to display results as JSON output. This output should be valid JSON."""

    def begin(self):
        """Force valid JSON by creating an *array* to represent all resources."""
        jsons.set_serializer(lambda o, **_: "", Configuration)
        jsons.set_serializer(lambda o, **_: "", ResourceType)
        self.config.file.write("[")

    def end(self):
        self.config.file.write("]")

    def end_resource(self, last: bool):
        self.config.file.write("\n" if last else ",\n")

    def print(self, resource, delim: str = "") -> None:
        """Print the resource out as JSON."""

        # TODO: strip out unwanted entries added by serialization (ex: local_configuration_vars)
        text = delim + jsons.dumps(
            resource,
            strip_privates=True,
            strip_nulls=False,
            strip_class_variables=True,
        )
        self.config.file.write(text)

    def print_next(self, last_one: bool) -> None:
        """Print a comma between resources but not for the last one."""
        self.config.file.write("\n" if last_one else ",\n")
