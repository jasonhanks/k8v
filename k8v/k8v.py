
import getopt
import sys

import kubernetes


import config
from resource_types import ResourceType


# delimeter to use for children resources
DELIM = "        "


class Viewer:
    """The Viewer is the main logic that will query the Kubernetes system and display the results."""

    def __init__(self, config: config.Config) -> None:
        self.config: config.Config = config


    def connect(self):
        """Load the Kubernetes configuration and setup API endpoint connections."""
        self.kubernetes_config = kubernetes.config.load_kube_config()
        self.api_client = kubernetes.client.ApiClient(self.kubernetes_config)
        self.api_core_v1 = kubernetes.client.CoreV1Api()
        self.api_apps_v1 = kubernetes.client.AppsV1Api(self.api_client)
        self.api_network_v1 = kubernetes.client.NetworkingV1Api()


    def filter_resources(self, resources):
        """Apply filtering logic to the specified resources."""

        # fitler by "includes" first
        for include in self.config.includes:
            resources = filter(lambda x: include in x.metadata.name, resources)

        # filter by label "selectors" next
        for label,value in self.config.selectors.items():
            resources = filter(lambda x: x.metadata.labels is not None and label in x.metadata.labels and x.metadata.labels[label] == value, resources)

        # exclude anything undesirable lastly
        for exclude in self.config.excludes:
            resources = filter(lambda x: exclude not in x.metadata.name, resources)
        return resources


    def get_api_handler(self, type: ResourceType) -> str:
        """Retrieve the API handler function to use for the specified namespace(s) and ResourceType."""
        if type == ResourceType.CONFIG_MAP:
            return self.api_core_v1.list_config_map_for_all_namespaces if self.config.namespaces is None else self.api_core_v1.list_namespaced_config_map
        elif type == ResourceType.DEPLOYMENTS:
            return self.api_apps_v1.list_deployment_for_all_namespaces if self.config.namespaces is None else self.api_apps_v1.list_namespaced_deployment
        elif type == ResourceType.DAEMON_SETS:
            return self.api_apps_v1.list_daemon_set_for_all_namespaces if self.config.namespaces is None else self.api_apps_v1.list_namespaced_daemon_set
        elif type == ResourceType.REPLICA_SETS:
            return self.api_apps_v1.list_replica_set_for_all_namespaces if self.config.namespaces is None else self.api_apps_v1.list_namespaced_replica_set
        elif type == ResourceType.PODS:
            return self.api_core_v1.list_pod_for_all_namespaces if self.config.namespaces is None else self.api_core_v1.list_namespaced_pod
        elif type == ResourceType.SECRETS:
            return self.api_core_v1.list_secret_for_all_namespaces if self.config.namespaces is None else self.api_core_v1.list_namespaced_secret
        elif type == ResourceType.INGRESS:
            return self.api_network_v1.list_ingress_for_all_namespaces if self.config.namespaces is None else self.api_network_v1.list_namespaced_ingress
        elif type == ResourceType.SERVICES:
            return self.api_core_v1.list_service_for_all_namespaces if self.config.namespaces is None else self.api_core_v1.list_namespaced_service
        else:
            return None


    def map_api_type(self, api_type: str) -> str:
        """Map the API class names to a more user friendly string to display."""
        if api_type == "V1ConfigMap":
            return "configmap"
        elif api_type == "V1Deployment":
            return "deployment"
        elif api_type == "V1Ingress":
            return "ingress"
        elif api_type == "V1Secret":
            return "secret"
        elif api_type == "V1ReplicaSet":
            return "replicaset"
        elif api_type == "V1DaemonSet":
            return "daemonset"
        elif api_type == "V1Pod":
            return "pod"
        elif api_type == "V1Service":
            return "service"
        else:
            return api_type


    def get_pod_data(self, resource) -> [list,list]:
        """Get any related configmap or secrets related to this resource."""

        # search for "envFrom" sections in the container definitions
        data: dict = { 'configmaps': [], 'secrets': [], 'pvcs': [], 'volumes': []}
        if hasattr(resource, 'spec') and hasattr(resource.spec, 'containers'):
            for container in resource.spec.containers:
                if hasattr(container, 'env_from') and container.env_from is not None:
                    for envFrom in container.env_from:
                        if hasattr(envFrom, 'config_map_ref') and envFrom.config_map_ref is not None:
                            data['configmaps'].append(envFrom.config_map_ref.name)
                        if hasattr(envFrom, 'secret_ref') and envFrom.secret_ref is not None:
                            data['secrets'].append(envFrom.secret_ref.name)

        # search through "volume" definitions
        if hasattr(resource, 'spec') and hasattr(resource.spec, 'volumes'):
            for volume in resource.spec.volumes:
                data['volumes'].append(volume)
                if volume.config_map is not None:
                    data['configmaps'].append(volume.config_map.name)
                elif volume.secret is not None:
                    data['secrets'].append(volume.secret.secret_name)
                elif volume.persistent_volume_claim is not None:
                    data['pvcs'].append(volume.persistent_volume_claim.claim_name)
        return data


    def get_label_text(self, resource) -> str:
        """Get the text that should be dispalyed for labels in all resources."""
        if resource.metadata.labels is None:
            return ""

        text: str = f"labels=["
        labels: list = []
        for label,value in resource.metadata.labels.items():
            labels.append(f"{label}={value}")
        text += f"{' '.join(labels)}] "
        return text


    def print(self, resource, type: ResourceType, delim: str = "") -> None:
        """Print out a resources and its information along with related resources."""
        if self.config.display_type == "brief":
            self.print_brief(resource, type, delim)
        elif self.config.display_type == "default":
            self.print_default(resource, type, delim)
        else:
            self.print_full(resource, type, delim)


    def print_brief(self, resource, type: ResourceType, delim: str = "") -> None:
        """Print the **brief** display version of a resource."""
        print(f"{delim}{self.map_api_type(resource.__class__.__name__)}/{resource.metadata.namespace}/{resource.metadata.name}")

    def print_default(self, resource, type: ResourceType, delim: str = "") -> None:
        """Print the **default** display version of a resource."""
        extended_info: str = ""
        post_info: str = ""

        extended_info += self.get_label_text(resource)
        extended_info += f"{'sa='+ resource.spec.service_account +' ' if hasattr(resource, 'spec') and hasattr(resource.spec, 'service_account') else ''}"
        if type in [ResourceType.CONFIG_MAP, ResourceType.SECRETS] and resource.data is not None and len(resource.data) > 0:
            extended_info += f"{'data='+ ', '.join(resource.data)}"

        elif type == ResourceType.PODS:
            pod_data = self.get_pod_data(resource)
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
            extended_info += f"type={resource.spec.type} cluster_ip={resource.spec.cluster_ip}"
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
                extended_info += f"host={rule.host} ("
                for path in rule.http.paths:
                    extended_info += f"{path.path} => {path.backend.service.name}:{path.backend.service.port.number}"
                extended_info += ") "

        extended_info = '('+extended_info+')' if len(extended_info) > 0 else extended_info
        if post_info != "":
            post_info = "\n"+ post_info
        print(f"{delim}{self.map_api_type(resource.__class__.__name__)}/{resource.metadata.namespace}/{resource.metadata.name} {extended_info}{post_info}")

        for related in self.search_for_related(resource, type):
            if type == ResourceType.DEPLOYMENTS:
                self.print(related, ResourceType.REPLICA_SETS, delim=delim+DELIM)
            elif type == ResourceType.DAEMON_SETS:
                self.print(related, ResourceType.PODS, delim=delim+DELIM)
            elif type == ResourceType.REPLICA_SETS:
                self.print(related, ResourceType.PODS, delim=delim+DELIM)

    def print_full(self, resource, type: ResourceType, delim: str = "") -> None:
        """Print the resource using the **full** display mode including related resources (configmaps, secrets, volumes, etc.) as children."""
        self.print_default(resource, type, delim)


    def search_for_related(self, resource, type: ResourceType) -> list:
        """Search for any related resources of the given type."""
        resources: list = []
        label_expr: str = ""

        if hasattr(resource, 'spec') and hasattr(resource.spec, 'selector'):
            selector = resource.spec.selector
            if hasattr(selector, 'match_expressions') and selector.match_expressions is not None and len(selector.match_expressions) > 0:
                pass # ignore since we cannot easily evaluate right now
            if hasattr(selector, 'match_labels'):
                label_count: int = len(selector.match_labels)-1
                for num, label in enumerate(selector.match_labels.items()):
                    label_expr += label[0] +"="+ label[1]
                    if num < label_count:
                        label_expr += ","
        elif resource.metadata.labels is not None and len(resource.metadata.labels) > 0:
            for num, label in enumerate(resource.metadata.labels):
                label_expr += label +"="+ resource.metadata.labels[label]
                if num < len(resource.metadata.labels)-1:
                    label_expr += ","

        if type == ResourceType.DEPLOYMENTS:
            resources = self.search(ResourceType.REPLICA_SETS, label_selector=label_expr)
        elif type == ResourceType.DAEMON_SETS:
            resources = self.search(ResourceType.PODS, label_selector=label_expr)
        elif type == ResourceType.REPLICA_SETS:
            resources = self.search(ResourceType.PODS, label_selector=label_expr)

        return resources


    def search(self, type: ResourceType, **kwargs) -> list:
        """Search for matching resources for the specified type."""
        resources = []

        # deterine which API call to use
        handler = self.get_api_handler(type)
        if handler is None:
            return resources 
            
        try:
            if self.config.verbose:
                print(f"Searching for {type.value[0]}") 

            if self.config.namespaces is None:
                api_response = handler(**kwargs)
                for d in api_response.items:
                    resources.append(d)
            else:
                for ns in self.config.namespaces:
                    api_response = handler(ns, **kwargs)
                    for d in api_response.items:
                        resources.append(d)
        except Exception as e:
            print(f"Exeception occurred while searching for resources ({type.value[0]}): {e}")
            raise e

        # apply filtering logic to matching resources
        return sorted(resources, key=lambda x: x.metadata.name)


    def view(self) -> None:
        """Use the input parameters to create a View of the desired resources and their relationships."""

        # show the input parameters
        if self.config.verbose:
            print(f"Display mode={self.config.display_type}, namespaces={self.config.namespaces}, resources={self.config.resources}, filters={self.config.includes}, selectors={self.config.selectors}")

        # setup the API handlers
        self.connect()

        # setup default namespace if no overrides specified
        if self.config.namespaces is not None and len(self.config.namespaces) == 0:
            self.config.namespaces.append("default")

        # default resources to search
        if len(self.config.resources) == 0:
            self.config.resources = [
                ResourceType.CONFIG_MAP,
                ResourceType.SECRETS,
                ResourceType.SERVICES,
                ResourceType.INGRESS,
                ResourceType.DAEMON_SETS,
                ResourceType.DEPLOYMENTS,
                ResourceType.PODS,
            ]

        # search for matching (and filtered) resources and print them out
        # using the desired display_mode.
        for type in self.config.resources:
            resources = self.search(type)
            for resource in self.filter_resources(resources):
                self.print(resource, type)


def usage() -> None:
    print()
    print("k8s viewer")
    print()
    print("Usage: viewer.py [-v|--verbose] [-d|--display <default|brief|full>] [-A|--all-namespaces] [-n|--namespace <ns>] [-e|--exclude <query>] [-r|--resource <type>] [-s|--selector <label=value>] [<search query>]")
    print()
    print("This utility is used to quickly see a lot of information about a Kubernetes context "
          "(default namespace is: default). This will display all the desired ")
    print("resources by type (default: deploy, daemonsets, replicasets, pods) and display various information about them.")
    print()
    print("display mode:")
    print("     -d | --display                  display mode used to display matches (default|brief|full)\n"
          "                                         default - shows most important resources on separate lines but summarizes others\n"
          "                                         brief   - shows one liner per resources with summary of related resources\n"
          "                                         full    - shows each resources as well as each related resources on a separate line"
    )
    print("     -v | --verbose                  display verbose logging messages")
    print()
    print("namespaces to search:")
    print("     -A | --all-namespaces           search for resources in all namespaces")
    print("     -n | --namespace <ns>           search for resources in the specified namespace (can be specified more than once). Note: default namespace must be specified if desired when using this option.")
    print()
    print("Note: by default only the default namespace is searched unless --all-namespaces or --namespace option is specified.")
    print()
    print("search criteria:")
    print("     -e | --exclude <query>          exclude resources by name substring matches (can be specified more than once)")
    print("     -i | --include <query>          include resources by name substring matches (can be specified more than once)")
    print("     -r | --resource <type>          specify resource types to search (can be specified more than once)")
    print("     -s | --selector <label=value>   select resources using labels (can be specified more than once)")
    print("     <query>                         same functionality as --include")
    print()
    print()
    print("Kubernetes Configuration:")
    print("By default k8v uses the KUBECONFIG environment variable for the Kubernetes cluster configuration. If not specified")
    print("it will default to ~/.kube/config.")
    print()
    print("Docker Usage:")
    print("Docker users will need to use the following syntax to pass their Kubernetes configuration as well as")
    print("other command line arguments. Otherwise the container will only display this message.")
    print()
    print("     # Example: run with default view")
    print("     docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest --")
    print()
    print("     # Example: run with brief view for a specific namespace")
    print("     docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -d brief -n metallb")
    print()
    print("     # Example: run while searching for a specific search term")
    print("     docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest heimdall")
    print()



def main(argv) -> None:
    """Main execution to setup the Viewer."""

    viewer: Viewer = Viewer(config.Config())
    try:
        opts, args = getopt.getopt(argv, "Avhd:f:e:i:n:r:s:", ["display", "all-namespaces", "exclude", "filter", "help" "include", "namespace",  "resource",  "selector", "verbose"])
    except getopt.GetoptError as e:
        usage()
        print(f"ERROR: {e}")
        print()
        sys.exit(2)

    for opt, arg in opts:
        # display the help
        if opt in ("-h", "--help"):
            usage()
            sys.exit()

        # display modes
        elif opt in ("-d", "--display"):
            viewer.config.display_type = arg
        elif opt in ("-v", "--verbose"):
            viewer.config.verbose = True

        # namespaces
        elif opt in ("-A", "--all-namespaces"):
            viewer.config.namespaces = None
        elif opt in ("-n", "--namespace"):
            if viewer.config.namespaces is None:
                viewer.config.namespaces = []
            viewer.config.namespaces.append(arg)

        # search criteria
        elif opt in ("-e", "--exclude"):
            viewer.config.excludes.append(arg)
        elif opt in ("-i", "--include"):
            viewer.config.includes.append(arg)
        elif opt in ("-r", "--resource"):
            for type in ResourceType:
                if arg in type.value:
                    viewer.config.resources.append(type)
        elif opt in ("-s", "--selector"):
            key, value = arg.split("=")
            viewer.config.selectors[key] = value

    # any remaining arguments are filter queries
    for arg in args:
        viewer.config.includes.append(arg)

    # Search for matching resources and display them
    viewer.view()


if __name__ == "__main__":
    main(sys.argv[1:])

