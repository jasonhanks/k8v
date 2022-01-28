import io
from typing import Protocol

from ansi.color import fg, bg
import ansi.color.fx as fx


import k8v


class Formatter(Protocol):
    """Formatters are used to display resources depending on the user's configuration."""

    def begin(self) -> None:
        """Start displaying resources."""

    def end(self) -> None:
        """Stop displaying resources."""

    def begin_resource(self) -> None:
        """Stop the Printer and cleanup anything if needed."""

    def end_resource(self, last: bool) -> None:
        """Stop the Printer and cleanup anything if needed."""

    def print(self, resource: object, delim: str) -> None:
        """Print the resources to the specified file."""


class FormatterBase(Formatter):
    def __init__(self, config: k8v.config.Config):
        self.config = config

    def begin_resource(self) -> None:
        pass

    def end_resource(self, last: bool) -> None:
        self.config.file.write("\n")

    def get_api_type(self, api_type: str) -> str:
        """Map the API class names to a more user friendly string to display.

        Args:
            api_type (str): Class name of the API object we need a friendly name for

        Returns:
            str: friendly name for the specified api_type
        """
        for k, v in self.config.handlers.items():
            for t, d in v.items():
                if "type" in d and d["type"] == api_type:
                    return t
        return None

    def get_pod_data(self, resource) -> [list, list]:
        """Get any related configmap or secrets related to this resource."""

        # search for "envFrom" sections in the container definitions
        data: dict = {"configmaps": [], "secrets": [], "pvcs": [], "volumes": []}
        if hasattr(resource, "spec") and hasattr(resource.spec, "containers"):
            for container in resource.spec.containers:
                if hasattr(container, "env_from") and container.env_from is not None:
                    for envFrom in container.env_from:
                        if (
                            hasattr(envFrom, "config_map_ref")
                            and envFrom.config_map_ref is not None
                        ):
                            data["configmaps"].append(envFrom.config_map_ref.name)
                        if (
                            hasattr(envFrom, "secret_ref")
                            and envFrom.secret_ref is not None
                        ):
                            data["secrets"].append(envFrom.secret_ref.name)

        # search through "volume" definitions
        if hasattr(resource, "spec") and hasattr(resource.spec, "volumes"):
            for volume in resource.spec.volumes:
                data["volumes"].append(volume)
                if volume.config_map is not None:
                    data["configmaps"].append(volume.config_map.name)
                elif volume.secret is not None:
                    data["secrets"].append(volume.secret.secret_name)
                elif volume.persistent_volume_claim is not None:
                    data["pvcs"].append(volume.persistent_volume_claim.claim_name)
        return data

    def get_text(self, key: str, text: str) -> str:
        """Format a message with the specified text before resetting the ANSI code."""

        # work with no schema selected
        if self.config.color_scheme == None:
            return text

        message = []
        for data in self.config.color_scheme[key]:
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
