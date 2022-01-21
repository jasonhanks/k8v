from typing import Protocol
import json
import sys

from ansi.color import fg, bg
import ansi.color.fx as fx

import kubernetes

from k8v.resource_types import ResourceType


class Printer(Protocol):
    """Printers are used to display resources depending on the user's configuration."""

    def begin() -> None:
        """Start the Printer so it can begin printing resources."""

    def end() -> None:
        """Stop the Printer and cleanup anything if needed."""

    def print(self, resource: object, **kwargs) -> None:
        """Print the specified resource out to the STDOUT.

        Args:
            resource (object): Kubernetes resource to be printed out.
        """


class PrinterBase(Printer):
    """The base class used by Printers that contain common behavior."""

    def __init__(self, viewer):
        self.viewer = viewer
        self.config = viewer.config

    def begin(self) -> None:
        """Start the Printer so that is it ready to begin printing objects.

        This will load the color-schemes.json file and setup the appropriate
        scheme that will be used by the Printer.

        Raises:
            e: Any IO related Exceptions raised during
        """
        try:
            schemes = json.load(open("etc/color-schemes.json"))["schemes"]
            if self.config.colors in schemes:
                self.colors = schemes[self.config.colors]
            else:
                self.colors = None
            self.handlers = json.load(open("etc/handlers.json"))
        except Exception as e:
            print(f"Exception occurred loading color schemes: {e}")
            raise e

    def end(self) -> None:
        """Stop the Printer and cleanup anything if needed."""
        pass

    def get_api_type(self, api_type: str) -> str:
        """Map the API class names to a more user friendly string to display.

        Args:
            api_type (str): Class name of the API object we need a friendly name for

        Returns:
            str: friendly name for the specified api_type
        """
        for k, v in self.handlers.items():
            if v["type"] == api_type:
                return k
        return None

    def get_ansi_text(self, key: str, text: str) -> str:
        """Format a message with the specified text before resetting the ANSI code."""

        # work with no schema selected
        if self.colors == None:
            return text

        message = []
        for data in self.colors[key]:
            src = None
            if data[0] == "fg":
                src = fg
            elif data[0] == "bg":
                src = bg
            elif data[0] == "fx":
                src = fx
            message.append(getattr(src, data[1]))
        message.append(text)
        message.append(fx.reset)
        return "".join(map(str, message))

    def get_label_text(self, resource) -> str:
        """Get the text that should be dispalyed for labels in all resources.

        Args:
            resource (dict): Dictionary containing JSON representation of API response.

        Returns:
            str: A str with information about the labels this resource has.
        """
        if resource.metadata.labels is None:
            return ""

        message: str = self.get_ansi_text("attr2_name", "labels")
        message += self.get_ansi_text("attr2_delim", "=[")
        for num, (label, value) in enumerate(resource.metadata.labels.items()):
            message += self.get_ansi_text("attr_name", label)
            message += self.get_ansi_text("attr_delim", "=")
            message += self.get_ansi_text("attr_value", value)
            if num < len(resource.metadata.labels) - 1:
                message += ", "
        message += self.get_ansi_text("attr2_delim", "] ")
        return message