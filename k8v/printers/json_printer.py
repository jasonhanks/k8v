from k8v.printers.printer import PrinterBase


class JsonPrinter(PrinterBase):
    def begin(self):
        super().begin()
        jsons.set_serializer(
            lambda o, **_: "", kubernetes.client.configuration.Configuration
        )
        jsons.set_serializer(lambda o, **_: "", ResourceType)
        print("[")

    def end(self):
        print("]")

    def print(self, resource, **kwargs,) -> None:
        """Print the resource out as JSON."""
        print(
            "    "
            + kwargs["delim"]
            + jsons.dumps(
                resource,
                strip_privates=True,
                strip_nulls=True,
                strip_class_variables=True,
            )
            + ("," if kwargs["index"] < kwargs["total"] else "")
        )

        # Ignore related resources unless they are needed
        if self.config.related == False:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            self.print(related, **kwargs)
