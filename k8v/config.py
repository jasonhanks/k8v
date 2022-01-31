import dataclasses
from io import IOBase
import json
import sys


import k8v


@dataclasses.dataclass
class Config:
    """Configuration variables used for the Viewer."""

    # color scheme
    colors: str = "default"

    # scheme to use at runtime
    color_scheme: dict = dataclasses.field(default_factory=dict)

    # delimeter to use for related resources
    delimeter: str = "        "

    # excludes list
    excludes: list = dataclasses.field(default_factory=list)

    # includes list
    includes: list = dataclasses.field(default_factory=list)

    # namespaces to search
    namespaces: list = dataclasses.field(default_factory=list)

    # output mode
    output: str = "default"

    # file used for output (default: STDOUT)
    file: IOBase = sys.stdout

    formatter = None

    # include related resources in results
    related: bool = False

    # resource types
    resources: list = dataclasses.field(default_factory=list)

    # label selectors
    selectors: dict = dataclasses.field(default_factory=dict)

    # verbose logging
    verbose: bool = False

    def load(self):
        try:
            schemes = json.load(open("etc/color-schemes.json"))["schemes"]
            if self.colors in schemes:
                self.color_scheme = schemes[self.colors]
            else:
                self.color_scheme = None
            self.handlers = json.load(open("etc/handlers.json"))
        except Exception as e:
            print(f"Exception occurred loading color schemes: {e}")
            raise e

        # setup default namespace if no overrides specified
        if self.namespaces is not None and len(self.namespaces) == 0:
            self.namespaces.append("default")

        # determine which resource types to search through
        if self.resources == None:
            self.resources = []
            for type in k8v.resource_types.ResourceType:
                self.resources.append(type)
        elif len(self.resources) == 0:
            self.resources = [
                k8v.resource_types.ResourceType.CONFIG_MAP,
                k8v.resource_types.ResourceType.SECRETS,
                k8v.resource_types.ResourceType.SERVICES,
                k8v.resource_types.ResourceType.INGRESS,
                k8v.resource_types.ResourceType.DAEMON_SETS,
                k8v.resource_types.ResourceType.STATEFUL_SETS,
                k8v.resource_types.ResourceType.REPLICA_SETS,
                k8v.resource_types.ResourceType.DEPLOYMENTS,
                k8v.resource_types.ResourceType.PODS,
                k8v.resource_types.ResourceType.CRONJOBS,
                k8v.resource_types.ResourceType.JOBS,
                k8v.resource_types.ResourceType.PERSISTENT_VOLUME,
                k8v.resource_types.ResourceType.PERSISTENT_VOLUME_CLAIM,
            ]

        # setup the formatter to use
        if self.output in ["brief", "b"]:
            self.formatter = k8v.formatters.brief_formatter.BriefFormatter(self)
        elif self.output in ["json", "j"]:
            self.formatter = k8v.formatters.json_formatter.JsonFormatter(self)
        else:
            self.formatter = k8v.formatters.default_formatter.DefaultFormatter(self)
