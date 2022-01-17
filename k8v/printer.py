import json

from ansi.color import fg, bg
import ansi.color.fx as fx

from resource_types import ResourceType


class Printer:

    def __init__(self, viewer):
        self.viewer = viewer
        self.config = viewer.config


    def connect(self) -> None:
        """Setup the Printer so that is it ready to begin printing objects.

        This will load the color-schemes.json file and setup the appropriate
        scheme that will be used by the Printer.

        Raises:
            e: Any IO related Exceptions raised during
        """
        try:
            schemes = json.load(open("k8v/color-schemes.json"))["schemes"]
            if self.config.colors in schemes:
                self.colors = schemes[self.config.colors]
            else:
                self.colors = None
        except Exception as e:
            print(f"Exception occurred loading color schemes: {e}")
            raise e


    def map_api_type(self, api_type: str) -> str:
        """Map the API class names to a more user friendly string to display.

        Args:
            api_type (str): Class name of the API object we need a friendly name for

        Returns:
            str: friendly name for the specified api_type
        """
        mapped_values = {
            "V1ConfigMap": "configmap",
            "V1Deployment": "deployment",
            "V1Ingress": "ingress",
            "V1Secret": "secret",
            "V1ReplicaSet": "replicaset",
            "V1DaemonSet": "daemonset",
            "V1Pod": "pod",
            "V1PersistentVolume": "persistentvolume",
            "V1PersistentVolumeClaim": "persistentvolumeclaim",
            "V1Service": "service",
        }
        return mapped_values[api_type] if api_type in mapped_values else api_type


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


    def print(self, resource, type: ResourceType, delim: str = "") -> None:
        """Print out a resources and its information along with related resources."""
        if self.config.output == "brief":
            self.print_brief(resource, type, delim)
        elif self.config.output == "default":
            self.print_default(resource, type, delim)
        else:
            self.print_full(resource, type, delim)


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


    def print_brief(self, resource, type: ResourceType, delim: str = "") -> None:
        """Print the **brief** display version of a resource."""
        message = delim + self.get_ansi_text(
            "type", self.map_api_type(resource.__class__.__name__)
        )
        message += "/"
        message += self.get_ansi_text("namespace", resource.metadata.namespace)
        message += "/"
        message += self.get_ansi_text("name", resource.metadata.name)
        print(message)


    def print_default(self, resource, type: ResourceType, delim: str = "") -> None:
        """Print the **default** display version of a resource."""
        extended_info: str = ""
        post_info: str = ""

        extended_info += self.get_label_text(resource)
        extended_info += f"{'sa='+ resource.spec.service_account +' ' if hasattr(resource, 'spec') and hasattr(resource.spec, 'service_account') else ''}"
        if (
            type in [ResourceType.CONFIG_MAP, ResourceType.SECRETS]
            and resource.data is not None
            and len(resource.data) > 0
        ):
            extended_info += f"{'data='+ ', '.join(resource.data)}"

        elif type == ResourceType.PERSISTENT_VOLUME:
            extended_info += f"storage_class={resource.spec.storage_class_name} access_modes={resource.spec.access_modes} reclaim={resource.spec.persistent_volume_reclaim_policy} capacity={resource.spec.capacity['storage']}"

        elif type == ResourceType.PERSISTENT_VOLUME_CLAIM:
            extended_info += f"storage_class={resource.spec.storage_class_name} access_modes={resource.spec.access_modes} capacity={resource.status.capacity['storage']} "
            extended_info += (
                f"volume={resource.spec.volume_name} phase={resource.status.phase}"
            )

        elif type == ResourceType.PODS:
            pod_data = self.viewer.searcher.get_pod_data(resource)
            extended_info += f"config_maps={', '.join(pod_data['configmaps']) if len(pod_data['configmaps']) > 0 else ''} "
            extended_info += f"secrets={', '.join(pod_data['secrets']) if len(pod_data['secrets']) > 0 else ''} "
            extended_info += f"pvc={', '.join(pod_data['pvcs']) if len(pod_data['pvcs']) > 0 else ''}"

        elif type == ResourceType.DEPLOYMENTS:
            if resource.status.replicas is not None and resource.status.replicas > 0:
                extended_info += f"replicas={resource.status.ready_replicas}/{resource.spec.replicas} (upd={resource.status.updated_replicas} avail={resource.status.available_replicas}) strategy={resource.spec.strategy.type}"
            if resource.spec.strategy.type == "RollingUpdate":
                extended_info += f" (max_surge={resource.spec.strategy.rolling_update.max_surge} max_unavailable={resource.spec.strategy.rolling_update.max_unavailable})"
            extended_info += f" generation={resource.metadata.generation}"

        elif type == ResourceType.SERVICES:
            extended_info += (
                f"type={resource.spec.type} cluster_ip={resource.spec.cluster_ip}"
            )
            extended_info += f"{'external_ip=' + resource.spec.external_i_ps if resource.spec.external_i_ps is not None else ''} "
            extended_info += f"{'loadbalancer_ip=' + resource.spec.load_balancer_ip if resource.spec.load_balancer_ip is not None else ''} "
            extended_info += f"ports=["
            for port in resource.spec.ports:
                extended_info += f"{str(port.port)}:{str(port.target_port)}/{port.protocol} {'nodeport='+str(port.node_port) if port.node_port is not None else ''}"
            extended_info += f"]"

        elif type == ResourceType.REPLICA_SETS:
            if resource.status.replicas is not None and resource.status.replicas > 0:
                extended_info += f"replicas={resource.status.ready_replicas}/{resource.spec.replicas} (avail={resource.status.available_replicas}) "
            extended_info += f"generation={resource.metadata.generation}"

        elif type == ResourceType.INGRESS:
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

        message = delim + self.get_ansi_text(
            "type", self.map_api_type(resource.__class__.__name__)
        )
        message += "/"
        if resource.metadata.namespace:
            message += self.get_ansi_text("namespace", resource.metadata.namespace)
            message += "/"
        message += self.get_ansi_text("name", resource.metadata.name)
        message += " "
        print(f"{message}{extended_info}{post_info}")

        for related in self.viewer.searcher.search_for_related(resource, type):
            if type == ResourceType.DEPLOYMENTS:
                self.print(
                    related, ResourceType.REPLICA_SETS, delim=self.viewer.delim + delim
                )
            elif type == ResourceType.DAEMON_SETS:
                self.print(related, ResourceType.PODS, delim=self.viewer.delim + delim)
            elif type == ResourceType.REPLICA_SETS:
                self.print(related, ResourceType.PODS, delim=self.viewer.delim + delim)


    def print_full(self, resource, type: ResourceType, delim: str = "") -> None:
        """Print the resource using the **full** display mode including related resources (configmaps, secrets, volumes, etc.) as children."""
        self.print_default(resource, type, delim)
