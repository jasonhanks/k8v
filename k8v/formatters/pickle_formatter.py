import pickle

from k8v.formatters.formatter import FormatterBase
from k8v.resource_types import ResourceType


class PickleFormatter(FormatterBase):
    """The Printer used to display results as Pickle output."""

    def end(self):
        self.config.file.close()

    def end_resource(self, resource):
        pass

    def print(self, resource, delim: str = "") -> None:
        """Print the resource out as JSON."""
        pickle.dump(resource, self.config.file)
