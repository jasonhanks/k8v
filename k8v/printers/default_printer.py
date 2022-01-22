import jsons
from io import StringIO

from k8v.resource_types import ResourceType
from k8v.printers.printer import PrinterBase


class DefaultPrinter(PrinterBase):
    """The Printer that is used by default."""

    def format_configmap(self, cm):
        if cm.data is not None and len(cm.data) > 0:
            return f"{'data='+ ', '.join(cm.data)}"
        return ""

    def format_deployment(self, deploy):
        msg = StringIO("")
        if deploy.status.replicas is not None and deploy.status.replicas > 0:
            msg.write(
                f"replicas={deploy.status.ready_replicas}/{deploy.spec.replicas} (upd={deploy.status.updated_replicas} avail={deploy.status.available_replicas}) strategy={deploy.spec.strategy.type}"
            )
        if deploy.spec.strategy.type == "RollingUpdate":
            msg.write(
                f" (max_surge={deploy.spec.strategy.rolling_update.max_surge} max_unavailable={deploy.spec.strategy.rolling_update.max_unavailable})"
            )
        msg.write(f" generation={deploy.metadata.generation}")
        return msg.getvalue()

    def format_ingress(self, ingress):
        msg = StringIO("")
        for rule in ingress.spec.rules:
            msg.write(f"host={rule.host} [")
            for path in rule.http.paths:
                msg.write(
                    f"{path.path}={path.backend.service.name}:{path.backend.service.port.number}"
                )
            msg.write("] ")
        return msg.getvalue()

    def format_replicaset(self, rs):
        msg = StringIO("")
        if rs.status.replicas is not None and rs.status.replicas > 0:
            msg.write(f"replicas=({rs.status.ready_replicas}/{rs.spec.replicas}) ")
            msg.write(f"avail={rs.status.available_replicas} ")
        msg.write(f"generation={rs.metadata.generation}")
        return msg.getvalue()

    def format_secret(self, secret):
        return self.format_configmap(secret)

    def format_service(self, service):
        msg = StringIO("")
        msg.write(f"type={service.spec.type} cluster_ip={service.spec.cluster_ip}")
        if service.spec.external_i_ps is not None:
            msg.write(f"{'external_ip=' + service.spec.external_i_ps} ")
        if service.spec.load_balancer_ip is not None:
            msg.write(f"{'loadbalancer_ip=' + service.spec.load_balancer_ip} ")
        msg.write(f"ports=[")
        for port in service.spec.ports:
            msg.write(
                f"{str(port.port)}:{str(port.target_port)}/{port.protocol} {'nodeport='+str(port.node_port) if port.node_port is not None else ''}"
            )
        msg.write(f"]")
        return msg.getvalue()

    def format_serviceaccount(self, sa):
        return f"secrets=[{', '.join(map(lambda x: x.name, sa.secrets))}]"

    def format_persistentvolume(self, pv):
        return f"storage_class={pv.spec.storage_class_name} access_modes={pv.spec.access_modes} reclaim={pv.spec.persistent_volume_reclaim_policy} capacity={pv.spec.capacity['storage']}"

    def format_persistentvolumeclaim(self, pvc):
        return f"storage_class={pvc.spec.storage_class_name} access_modes={pvc.spec.access_modes} capacity={pvc.status.capacity['storage']} volume={pvc.spec.volume_name} phase={pvc.status.phase}"

    def format_pod(self, pod):
        pod_data = self.viewer.searcher.get_pod_data(pod)
        return f"config_maps={', '.join(pod_data['configmaps']) if len(pod_data['configmaps']) > 0 else ''} secrets={', '.join(pod_data['secrets']) if len(pod_data['secrets']) > 0 else ''} pvc={', '.join(pod_data['pvcs']) if len(pod_data['pvcs']) > 0 else ''}"

    def format_statefulsets(self, ss):
        msg = StringIO("")
        if ss.status.replicas is not None and ss.status.replicas > 0:
            msg.write(
                f"replicas={ss.status.ready_replicas}/{ss.spec.replicas} (upd={ss.status.updated_replicas} avail={ss.status.current_replicas}) strategy={ss.spec.update_strategy.type}"
            )
        msg.write(f"generation={ss.metadata.generation}")
        return msg.getvalue()

    def print(self, resource, **kwargs) -> None:
        """Print the **default** display version of a resource."""
        details = StringIO("")

        # write common things first
        details.write(self.get_label_text(resource))
        if hasattr(resource, "spec") and hasattr(resource.spec, "service_account"):
            details.write(f"sa={resource.spec.service_account} ")

        # Use format_<type> methods if they exist
        if hasattr(self, f"format_{resource.type.value[0]}"):
            details.write(getattr(self, f"format_{resource.type.value[0]}")(resource))

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
        print(f"{message.getvalue()}({details.getvalue()})")

        # Ignore related resources unless they are needed
        if not self.config.related:
            return

        kwargs["delim"] = kwargs["delim"] + self.config.delimeter
        for related in self.viewer.searcher.search_for_related(resource, resource.type):
            self.print(related, **kwargs)
