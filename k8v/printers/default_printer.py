import jsons
from io import StringIO
from string import Template

from k8v.resource_types import ResourceType
from k8v.printers.printer import PrinterBase


class DefaultPrinter(PrinterBase):
    """The Printer that is used by default."""

    def print(self, resource, **kwargs) -> None:
        """Print the **default** display version of a resource."""
        extended = StringIO("")
        post = StringIO("")

        extended.write(self.get_label_text(resource))
        extended.write(
            f"{'sa='+ resource.spec.service_account +' ' if hasattr(resource, 'spec') and hasattr(resource.spec, 'service_account') else ''}"
        )
        if (
            resource.type in [ResourceType.CONFIG_MAP, ResourceType.SECRETS]
            and resource.data is not None
            and len(resource.data) > 0
        ):
            extended.write(f"{'data='+ ', '.join(resource.data)}")
        elif resource.type == ResourceType.PERSISTENT_VOLUME:
            extended.write(
                f"storage_class={resource.spec.storage_class_name} access_modes={resource.spec.access_modes} reclaim={resource.spec.persistent_volume_reclaim_policy} capacity={resource.spec.capacity['storage']}"
            )
        elif resource.type == ResourceType.PERSISTENT_VOLUME_CLAIM:
            extended.write(
                f"storage_class={resource.spec.storage_class_name} access_modes={resource.spec.access_modes} capacity={resource.status.capacity['storage']} "
            )
            extended.write(
                f"volume={resource.spec.volume_name} phase={resource.status.phase}"
            )
        elif resource.type == ResourceType.PODS:
            pod_data = self.viewer.searcher.get_pod_data(resource)
            extended.write(
                f"config_maps={', '.join(pod_data['configmaps']) if len(pod_data['configmaps']) > 0 else ''} "
            )
            extended.write(
                f"secrets={', '.join(pod_data['secrets']) if len(pod_data['secrets']) > 0 else ''} "
            )
            extended.write(
                f"pvc={', '.join(pod_data['pvcs']) if len(pod_data['pvcs']) > 0 else ''}"
            )
        elif resource.type == ResourceType.DEPLOYMENTS:
            if resource.status.replicas is not None and resource.status.replicas > 0:
                extended.write(
                    f"replicas={resource.status.ready_replicas}/{resource.spec.replicas} (upd={resource.status.updated_replicas} avail={resource.status.available_replicas}) strategy={resource.spec.strategy.type}"
                )
            if resource.spec.strategy.type == "RollingUpdate":
                extended.write(
                    f" (max_surge={resource.spec.strategy.rolling_update.max_surge} max_unavailable={resource.spec.strategy.rolling_update.max_unavailable})"
                )
            extended.write(f" generation={resource.metadata.generation}")
        elif resource.type == ResourceType.SERVICE_ACCOUNTS:
            extended.write(
                f"secrets=[{', '.join(map(lambda x: x.name, resource.secrets))}]"
            )
        elif resource.type == ResourceType.STATEFUL_SETS:
            if resource.status.replicas is not None and resource.status.replicas > 0:
                extended.write(
                    f"replicas={resource.status.ready_replicas}/{resource.spec.replicas} (upd={resource.status.updated_replicas} avail={resource.status.current_replicas}) strategy={resource.spec.update_strategy.type}"
                )
            extended.write(f" generation={resource.metadata.generation}")
        elif resource.type == ResourceType.SERVICES:
            extended.write(
                f"type={resource.spec.type} cluster_ip={resource.spec.cluster_ip}"
            )
            extended.write(
                f"{'external_ip=' + resource.spec.external_i_ps if resource.spec.external_i_ps is not None else ''} "
            )
            extended.write(
                f"{'loadbalancer_ip=' + resource.spec.load_balancer_ip if resource.spec.load_balancer_ip is not None else ''} "
            )
            extended.write(f"ports=[")
            for port in resource.spec.ports:
                extended.write(
                    f"{str(port.port)}:{str(port.target_port)}/{port.protocol} {'nodeport='+str(port.node_port) if port.node_port is not None else ''}"
                )
            extended.write(f"]")
        elif resource.type == ResourceType.REPLICA_SETS:
            if resource.status.replicas is not None and resource.status.replicas > 0:
                extended.write(
                    f"replicas={resource.status.ready_replicas}/{resource.spec.replicas} (avail={resource.status.available_replicas}) "
                )
            extended.write(f"generation={resource.metadata.generation}")
        elif resource.type == ResourceType.INGRESS:
            for rule in resource.spec.rules:
                extended.write(f"host={rule.host} [")
                for path in rule.http.paths:
                    extended.write(
                        f"{path.path}={path.backend.service.name}:{path.backend.service.port.number}"
                    )
                extended.write("] ")
        if post.read() != "":
            post.write("\n")

        type_text = self.get_api_type(resource.__class__.__name__)
        message = StringIO("")
        message.write(kwargs["delim"])
        message.write(self.get_ansi_text("type", type_text))
        message.write("/")
        if resource.metadata.namespace:
            message.write(self.get_ansi_text("namespace", resource.metadata.namespace))
            message.write("/")
        message.write(self.get_ansi_text("name", resource.metadata.name))
        message.write(" ")
        print(f"{message.getvalue()}{extended.getvalue()}{post.getvalue()}")

        # Ignore related resources unless they are needed
        if not self.config.related:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            self.print(related, **kwargs)
