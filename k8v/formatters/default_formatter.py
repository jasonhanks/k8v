import jsons
from io import StringIO

from k8v.resource_types import ResourceType
from k8v.formatters.formatter import FormatterBase


class DefaultFormatter(FormatterBase):
    """The Printer that is used by default."""

    def format(self, name, value, **kwargs):
        # defaults for kwargs
        if "key" not in kwargs:
            kwargs["key"] = "attr2"
        if "start" not in kwargs:
            kwargs["start"] = "="
        if "end" not in kwargs:
            kwargs["end"] = ""

        msg: StringIO = StringIO("")
        msg.write(self.get_text(f"{kwargs['key']}_name", name))
        msg.write(self.get_text(f"{kwargs['key']}_delim", kwargs["start"]))
        msg.write(self.get_text(f"{kwargs['key']}_value", str(value)))
        msg.write(self.get_text(f"{kwargs['key']}_delim", kwargs["end"]))
        return msg.getvalue()

    def format_clusterrole(self, cr):
        pairs: list = list()
        pairs.append(self.format("aggregation_rule", cr.aggregation_rule is not None))
        pairs.append(self.format("rules", len(cr.rules)))
        return " ".join(pairs)

    def format_clusterrolebinding(self, crb):
        pairs: list = list()
        pairs.append(self.format("role_ref", crb.role_ref.name))
        if crb.subjects is not None:
            pairs.append(
                self.format(
                    "subjects", list(map(lambda o: f"{o.kind}={o.name}", crb.subjects))
                )
            )
        return " ".join(pairs)

    def format_configmap(self, cm):
        pairs: list = list()
        if cm.data is not None and len(cm.data) > 0:
            pairs.append(self.format("data", ", ".join(cm.data), start="=[", end="]"))
        return " ".join(pairs)

    def format_deployment(self, deploy):
        pairs: list = []
        if deploy.status.replicas is not None and deploy.status.replicas > 0:
            pairs.append(
                self.format(
                    "replicas",
                    f"{deploy.status.ready_replicas}/{deploy.spec.replicas}",
                )
            )
            pairs.append(self.format("upd", deploy.status.updated_replicas))
            pairs.append(self.format("avail", deploy.status.available_replicas))
            pairs.append(self.format("strategy", deploy.spec.strategy.type))

        if deploy.spec.strategy.type == "RollingUpdate":
            pairs.append(
                self.format("max_surge", deploy.spec.strategy.rolling_update.max_surge)
            )
            pairs.append(
                self.format(
                    "max_unavailable",
                    deploy.spec.strategy.rolling_update.max_unavailable,
                )
            )
        pairs.append(self.format("generation", deploy.metadata.generation))
        return " ".join(pairs)

    def format_ingress(self, ingress):
        pairs: list = []
        if "kubernetes.io/ingress.class" in ingress.metadata.annotations:
            pairs.append(
                self.format(
                    "class",
                    ingress.metadata.annotations["kubernetes.io/ingress.class"],
                )
            )
        else:
            pairs.append(self.format("class", ingress.spec.ingressClassName))
        for rule in ingress.spec.rules:
            paths: list = list()
            for path in rule.http.paths:
                paths.append(
                    self.format(
                        path.path,
                        f"{path.backend.service.name}:{path.backend.service.port.number}",
                    )
                )
            pairs.append(self.format(rule.host, " ".join(paths), start="=[", end="]"))
        return " ".join(pairs)

    def format_labels(self, resource) -> str:
        if not hasattr(resource.metadata, "labels") or resource.metadata.labels is None:
            return ""
        labels: list = list()
        for label, value in resource.metadata.labels.items():
            labels.append(self.format(label, value))
        return self.format("labels", " ".join(labels), start="=[", end="]") + " "

    def format_replicaset(self, rs):
        pairs: list = list()
        if rs.status.replicas is not None and rs.status.replicas > 0:
            pairs.append(
                self.format(
                    "replicas", f"{rs.status.ready_replicas}/{rs.spec.replicas}"
                )
            )
            pairs.append(self.format("avail", rs.status.available_replicas))

        pairs.append(self.format("generation", rs.metadata.generation))
        return " ".join(pairs)

    def format_role(self, cr):
        return self.format("rules", len(cr.rules))

    def format_rolebinding(self, rb):
        pairs: list = list()
        pairs.append(self.format("role_ref", rb.role_ref.name))
        if rb.subjects is not None:
            pairs.append(
                self.format(
                    "subjects", list(map(lambda o: f"{o.kind}={o.name}", rb.subjects))
                )
            )
        return " ".join(pairs)

    def format_secret(self, secret):
        return self.format_configmap(secret)

    def format_service(self, service):
        pairs: list = list()
        ports: list = list()

        pairs.append(self.format("type", service.spec.type))
        pairs.append(self.format("cluster_ip", service.spec.cluster_ip))

        if service.spec.external_i_ps is not None:
            pairs.append(self.format("external_ip", service.spec.external_i_ps))
        if service.spec.load_balancer_ip is not None:
            pairs.append(self.format("loadbalancer_ip", service.spec.load_balancer_ip))
        for port in service.spec.ports:
            ports.append(
                self.format(
                    str(port.port),
                    f"{str(port.target_port)}/{port.protocol} {self.format('nodeport', str(port.node_port)) if port.node_port is not None else ''}",
                )
            )
        pairs.append(self.format("ports", ", ".join(ports), start="=[", end="]"))
        return " ".join(pairs)

    def format_serviceaccount(self, sa):
        if sa.secrets is not None and len(sa.secrets) > 0:
            return self.format(
                "secrets",
                " ".join(map(lambda o: o.name, sa.secrets)),
                start="=[",
                end="]",
            )
        return ""

    def format_persistentvolume(self, pv):
        pairs: list = list()
        pairs.append(self.format("storage_class", pv.spec.storage_class_name))
        pairs.append(self.format("access_modes", pv.spec.access_modes))
        pairs.append(self.format("capacity", pv.spec.capacity["storage"]))
        pairs.append(self.format("reclaim", pv.spec.persistent_volume_reclaim_policy))
        return " ".join(pairs)

    def format_persistentvolumeclaim(self, pvc):
        pairs: list = list()
        pairs.append(self.format("access_modes", pvc.spec.storage_class_name))
        pairs.append(self.format("storage_class", pvc.spec.access_modes))
        pairs.append(self.format("capacity", pvc.status.capacity["storage"]))
        pairs.append(self.format("volume", pvc.spec.volume_name))
        pairs.append(self.format("phase", pvc.status.phase))
        return " ".join(pairs)

    def format_pod(self, pod):
        data = self.get_pod_data(pod)
        pairs: list = list()
        if len(data["configmaps"]) > 0:
            pairs.append(
                self.format("configmaps", data["configmaps"], start="=[", end="]")
            )
        if len(data["secrets"]) > 0:
            pairs.append(self.format("secrets", data["secrets"], start="=[", end="]"))
        if len(data["pvcs"]) > 0:
            pairs.append(self.format("pvcs", data["pvcs"], start="=[", end="]"))
        return " ".join(pairs)

    def format_statefulset(self, ss):
        pairs: list = list()
        pairs.append(self.format("strategy", ss.spec.update_strategy.type))
        pairs.append(self.format("generation", str(ss.metadata.generation)))
        if ss.status.replicas is not None and ss.status.replicas > 0:
            pairs.append(
                self.format(
                    "replicas",
                    f"{ss.status.ready_replicas}/{ss.spec.replicas}",
                    start="(",
                    end=")",
                )
            )
            pairs.append(
                self.format(
                    "upd",
                    str(ss.status.updated_replicas),
                    start="(",
                    end=")",
                )
            )
            pairs.append(
                self.format(
                    "avail",
                    str(ss.status.current_replicas),
                    start="(",
                    end=")",
                )
            )
        return " ".join(pairs)

    def print(self, resource, delim="") -> None:
        """Print the **default** display version of a resource."""
        details = StringIO("")

        # write common things first
        details.write(self.format_labels(resource))
        if hasattr(resource, "spec") and hasattr(resource.spec, "service_account"):
            details.write(self.format("sa", resource.spec.service_account) + " ")

        # Use format_<type> methods if they exist
        if hasattr(self, f"format_{resource.type.value[0]}"):
            details.write(getattr(self, f"format_{resource.type.value[0]}")(resource))

        type_text = self.get_api_type(resource.__class__.__name__)
        message = StringIO("")
        message.write(delim)
        message.write(self.get_text("type", resource.type.value[0]))
        message.write("/")
        if resource.metadata.namespace:
            message.write(self.get_text("namespace", resource.metadata.namespace))
            message.write("/")
        message.write(self.get_text("name", resource.metadata.name))
        message.write(" ")
        self.config.file.write(f"{message.getvalue()}({details.getvalue()})")
