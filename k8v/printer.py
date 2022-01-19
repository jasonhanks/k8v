from typing import Protocol
import json
import jsons
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
        mapped_values = {
            "V1ConfigMap": ResourceType.CONFIG_MAP.value[0],
            "V1Deployment": ResourceType.DEPLOYMENTS.value[0],
            "V1Ingress": ResourceType.INGRESS.value[0],
            "V1Secret": ResourceType.SECRETS.value[0],
            "V1ReplicaSet": ResourceType.REPLICA_SETS.value[0],
            "V1DaemonSet": ResourceType.DAEMON_SETS.value[0],
            "V1Pod": ResourceType.PODS.value[0],
            "V1PersistentVolume": ResourceType.PERSISTENT_VOLUME.value[0],
            "V1PersistentVolumeClaim": ResourceType.PERSISTENT_VOLUME_CLAIM.value[0],
            "V1Service": ResourceType.SERVICES.value[0],
        }
        return mapped_values[api_type] if api_type in mapped_values else api_type

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


class BriefPrinter(PrinterBase):
    """The Printer that is used for the *brief* output type."""

    def print(self, resource, **kwargs) -> None:
        """Print out a resources and its information along with related resources."""
        message = kwargs["delim"] + self.get_ansi_text(
            "type", self.get_api_type(resource.__class__.__name__)
        )
        message += "/"
        message += f"{self.get_ansi_text('namespace', resource.metadata.namespace) +'/' if resource.metadata.namespace else ''}"
        message += self.get_ansi_text("name", resource.metadata.name)
        print(message)

        # Ignore related resources unless they are needed
        if self.config.related == False:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            self.print(related, **kwargs)


class DefaultPrinter(PrinterBase):
    """The Printer that is used by default."""

    def print(self, resource, **kwargs) -> None:
        """Print the **default** display version of a resource."""
        extended_info: str = ""
        post_info: str = ""

        extended_info += self.get_label_text(resource)
        extended_info += f"{'sa='+ resource.spec.service_account +' ' if hasattr(resource, 'spec') and hasattr(resource.spec, 'service_account') else ''}"
        if (
            resource.type in [ResourceType.CONFIG_MAP, ResourceType.SECRETS]
            and resource.data is not None
            and len(resource.data) > 0
        ):
            extended_info += f"{'data='+ ', '.join(resource.data)}"

        elif resource.type == ResourceType.PERSISTENT_VOLUME:
            extended_info += f"storage_class={resource.spec.storage_class_name} access_modes={resource.spec.access_modes} reclaim={resource.spec.persistent_volume_reclaim_policy} capacity={resource.spec.capacity['storage']}"

        elif resource.type == ResourceType.PERSISTENT_VOLUME_CLAIM:
            extended_info += f"storage_class={resource.spec.storage_class_name} access_modes={resource.spec.access_modes} capacity={resource.status.capacity['storage']} "
            extended_info += (
                f"volume={resource.spec.volume_name} phase={resource.status.phase}"
            )

        elif resource.type == ResourceType.PODS:
            pod_data = self.viewer.searcher.get_pod_data(resource)
            extended_info += f"config_maps={', '.join(pod_data['configmaps']) if len(pod_data['configmaps']) > 0 else ''} "
            extended_info += f"secrets={', '.join(pod_data['secrets']) if len(pod_data['secrets']) > 0 else ''} "
            extended_info += f"pvc={', '.join(pod_data['pvcs']) if len(pod_data['pvcs']) > 0 else ''}"

        elif resource.type == ResourceType.DEPLOYMENTS:
            if resource.status.replicas is not None and resource.status.replicas > 0:
                extended_info += f"replicas={resource.status.ready_replicas}/{resource.spec.replicas} (upd={resource.status.updated_replicas} avail={resource.status.available_replicas}) strategy={resource.spec.strategy.type}"
            if resource.spec.strategy.type == "RollingUpdate":
                extended_info += f" (max_surge={resource.spec.strategy.rolling_update.max_surge} max_unavailable={resource.spec.strategy.rolling_update.max_unavailable})"
            extended_info += f" generation={resource.metadata.generation}"

        elif resource.type == ResourceType.SERVICES:
            extended_info += (
                f"type={resource.spec.type} cluster_ip={resource.spec.cluster_ip}"
            )
            extended_info += f"{'external_ip=' + resource.spec.external_i_ps if resource.spec.external_i_ps is not None else ''} "
            extended_info += f"{'loadbalancer_ip=' + resource.spec.load_balancer_ip if resource.spec.load_balancer_ip is not None else ''} "
            extended_info += f"ports=["
            for port in resource.spec.ports:
                extended_info += f"{str(port.port)}:{str(port.target_port)}/{port.protocol} {'nodeport='+str(port.node_port) if port.node_port is not None else ''}"
            extended_info += f"]"

        elif resource.type == ResourceType.REPLICA_SETS:
            if resource.status.replicas is not None and resource.status.replicas > 0:
                extended_info += f"replicas={resource.status.ready_replicas}/{resource.spec.replicas} (avail={resource.status.available_replicas}) "
            extended_info += f"generation={resource.metadata.generation}"

        elif resource.type == ResourceType.INGRESS:
            for rule in resource.spec.rules:
                extended_info += f"host={rule.host} ["
                for path in rule.http.paths:
                    extended_info += f"{path.path}={path.backend.service.name}:{path.backend.service.port.number}"
                extended_info += "] "

        extended_info = (
            "(" + extended_info + ")" if len(extended_info) > 0 else extended_info
        )
        if post_info != "":
            post_info = "\n" + post_info

        message = kwargs["delim"] + self.get_ansi_text(
            "type", self.get_api_type(resource.__class__.__name__)
        )
        message += "/"
        if resource.metadata.namespace:
            message += self.get_ansi_text("namespace", resource.metadata.namespace)
            message += "/"
        message += self.get_ansi_text("name", resource.metadata.name)
        message += " "
        print(f"{message}{extended_info}{post_info}")

        # Ignore related resources unless they are needed
        if self.config.related == False:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            if resource.type == ResourceType.DEPLOYMENTS:
                self.print(related, **kwargs)
            elif resource.type == ResourceType.DAEMON_SETS:
                self.print(
                    related,
                    **kwargs,
                )
            elif resource.type == ResourceType.REPLICA_SETS:
                self.print(
                    related,
                    **kwargs,
                )


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

    def print(
        self,
        resource,
        **kwargs,
    ) -> None:
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


class FullPrinter(DefaultPrinter):
    """The Printer that is used for the *full* output type."""

    pass
