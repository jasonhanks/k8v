import jsons

import kubernetes
from kubernetes.client.configuration import Configuration

from k8v.printers.printer import PrinterBase
from k8v.resource_types import ResourceType


class JsonPrinter(PrinterBase):
    """The Printer used to display results as JSON output. This output should be valid JSON."""

    def begin(self):
        super().begin()
        jsons.set_serializer(lambda o, **_: "", Configuration)
        jsons.set_serializer(lambda o, **_: "", ResourceType)
        print("[")

    def end(self):
        print("]")

    def print(self, resource, **kwargs) -> None:
        """Print the resource out as JSON."""

        text = (
            self.config.delimeter
            + kwargs["delim"]
            + jsons.dumps(
                resource,
                strip_privates=True,
                strip_nulls=True,
                strip_class_variables=True,
            )
            + ("," if kwargs["index"] < kwargs["total"] else "")
        )

        if kwargs.get("out") is not None:
            kwargs["out"].write(text)
        else:
            print(text)

        # Ignore related resources unless they are requested
        if not self.config.related:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            self.print(related, **kwargs)
