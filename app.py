import getopt
import sys

import k8v


def usage() -> None:
    """Display the command line usage help screen."""

    print()
    print("NAME")
    print("        k8v - view Kubernetes cluster resources")
    print()
    print("SYNOPSIS")
    print("        k8v [OPTION]... [QUERY]...")
    print()
    print("DESCRIPTION")
    print(
        "        This utility is used to quickly see a lot of information about a Kubernetes context "
        "(default namespace is: default). This will display all the desired "
    )
    print(
        "        resources by type (default: configmap, deployments, daemonsets, ingresses, persistentvolume, persistentvolumeclaim, replicasets, pods, secrets, "
    )
    print(
        "        services, and statefulset) and display various information about them."
    )
    print()
    print(
        "        Filtering capabilities are provided which can either exclude or include matching resources as needed. By default any arguments that are not available "
    )
    print(
        "        options below will be used as search criteria (same behavior as --include option)."
    )
    print()
    print("        -c, --colors=SCHEME")
    print(
        "                colorize the output; SCHEME can be 'default' (default if omitted), or 'none' for no color output\n"
    )
    print("        -o, --output=TYPE")
    print(
        "                output mode used to display matching resources; TYPE can be 'wide' (default if omitted), 'brief' for list of resource, or 'json' for full information\n"
    )
    print("        -f, --file")
    print(
        "                specify a filename to be used for output (STDOUT if omitted)"
    )
    print()
    print("        -A, --all-namespaces")
    print("                search for matching resources that exist in all namespaces")
    print()
    print("        -n, --namespace=NAMESPACE")
    print(
        "                search for resources in the specified namespace; NAMESPACE can be any valid namespace ('default' if omitted); can be specified more than once"
    )
    print()
    print("        -R, --all-resources")
    print("                search for matching resources with any supported type")
    print()
    print("        -r, --resource=TYPE")
    print(
        "                search for matching resources with the specified type; can be specified more than once"
    )
    print()
    print("        -e, --exclude=QUERY")
    print(
        "                exclude any matching resources who's name includes the specified QUERY; can be specified more than once"
    )
    print()
    print("        -i, --include=QUERY")
    print(
        "                include any matching resources who's name includes the specified QUERY; can be specified more than once"
    )
    print()
    print("        -s, --selector=SELECTOR")
    print(
        "                include any matching resources who have a matching label matching the SELECTOR (e.g. LABEL=value); can be specified more than once"
    )
    print()
    print("         -t, --all-related")
    print("                display related resources in a hierachy structure")
    print()
    print("        -v, --verbose")
    print("                display verbose logging messages")
    print()
    print("KUBERNETES:")
    print(
        "        By default k8v uses the KUBECONFIG environment variable for the Kubernetes cluster configuration. If not specified it will default to ~/.kube/config."
    )
    print()
    print("DOCKER")
    print(
        "        Docker users will need to use the following syntax to pass their Kubernetes configuration as well as other command line arguments, otherwise the "
    )
    print("        container will only display this message.")
    print()
    print("        # Example: run with default view")
    print("        docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest --")
    print()
    print("        # Example: run with brief view for a specific namespace")
    print(
        "        docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -o brief -n metallb"
    )
    print()
    print("        # Example: run while searching for a specific search term")
    print(
        "        docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest heimdall"
    )
    print()
    print("    Exit status:")
    print("        0      if OK,")
    print(
        "        1      if problems are encountered (e.g., cannot connect to Kubernetes cluster, cannot locate color scheme, etc.)"
    )
    print()
    print("AUTHOR:")
    print("        Written by Jason Hanks.")
    print()
    print("REPORTING BUGS:")
    print("        GitHub Project: https://github.com/jasonhanks/k8v.")
    print()
    print("LICENSE:")
    print(
        "        This project is distributed under an MIT License. See included LICENSE file for details."
    )
    print()


def main(argv: list) -> None:
    """Main execution to setup the Viewer."""

    viewer: k8v.viewer.Viewer = k8v.viewer.Viewer()
    try:
        opts, args = getopt.getopt(
            argv,
            "ARtvhc:e:f:i:n:o:r:s:",
            [
                "all-related",
                "all-resources",
                "colors",
                "all-namespaces",
                "exclude",
                "file",
                "help",
                "include",
                "namespace",
                "output",
                "resource",
                "selector",
                "verbose",
            ],
        )
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
        elif opt in ("-c", "--colors"):
            viewer.config.colors = arg
        elif opt in ("-o", "--output"):
            viewer.config.output = arg
        elif opt in ("-v", "--verbose"):
            viewer.config.verbose = True
        elif opt in ("-f", "--file"):
            viewer.config.file = open(arg, "w")

        # namespaces
        elif opt in ("-A", "--all-namespaces"):
            viewer.config.namespaces = None
        elif opt in ("-n", "--namespace"):
            if viewer.config.namespaces is None:
                viewer.config.namespaces = []
            viewer.config.namespaces.append(arg)

        # search criteria
        elif opt in ("-t", "--all-related"):
            viewer.config.related = True
        elif opt in ("-e", "--exclude"):
            viewer.config.excludes.append(arg)
        elif opt in ("-i", "--include"):
            viewer.config.includes.append(arg)
        elif opt in ("-R", "--all-resources"):
            viewer.config.resources = None
        elif opt in ("-r", "--resource"):
            for type in k8v.resource_types.ResourceType:
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
