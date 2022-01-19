import getopt
import sys

import k8v


def usage() -> None:
    """Display the command line usage help screen."""

    print()
    print("k8v - kubernetes viewer")
    print()
    print(
        "Usage: k8v.py [-vA] [-o <default|brief|full>] [-n <ns>] [-e <query>] [-r <type>] [-s <label=value>] [<query>]"
    )
    print()
    print(
        "This utility is used to quickly see a lot of information about a Kubernetes context "
        "(default namespace is: default). This will display all the desired "
    )
    print(
        "resources by type (default: deploy, daemonsets, replicasets, pods) and display various information about them."
    )
    print()
    print("display mode:")
    print(
        "     -c | --colors <scheme>          use the named color scheme (specified in k8s/color-scheme.json) or use 'none' for plain text"
    )
    print(
        "     -o | --output                   output mode used to display matching resources (default|brief|full)\n"
        "                                         default - shows most important resources on separate lines but summarizes others\n"
        "                                         brief   - shows one liner per resources with summary of related resources\n"
        "                                         full    - shows each resources as well as each related resources on a separate line"
        "                                         json    - shows the list of matching resources as JSON"
    )
    print("     -v | --verbose                  display verbose logging messages")
    print()
    print("namespaces to search:")
    print("     -A | --all-namespaces           search for resources in all namespaces")
    print(
        "     -n | --namespace <ns>           search for resources in the specified namespace (can be specified more than once)"
    )
    print()
    print(
        "Note: by default only the default namespace is searched unless --all-namespaces or --namespace option is specified."
    )
    print()
    print("search criteria:")
    print(
        "     -e | --exclude <query>          exclude resources by name substring matches (can be specified more than once)"
    )
    print(
        "     -i | --include <query>          include resources by name substring matches (can be specified more than once)"
    )
    print(
        "     -r | --resource <type>          specify resource types to search (can be specified more than once)"
    )
    print(
        "     -s | --selector <label=value>   select resources using labels (can be specified more than once)"
    )
    print("     <query>                         same functionality as --include")
    print()
    print()
    print("Kubernetes Configuration:")
    print(
        "By default k8v uses the KUBECONFIG environment variable for the Kubernetes cluster configuration. If not specified"
    )
    print("it will default to ~/.kube/config.")
    print()
    print("Docker Usage:")
    print(
        "Docker users will need to use the following syntax to pass their Kubernetes configuration as well as"
    )
    print(
        "other command line arguments. Otherwise the container will only display this message."
    )
    print()
    print("     # Example: run with default view")
    print("     docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest --")
    print()
    print("     # Example: run with brief view for a specific namespace")
    print(
        "     docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -d brief -n metallb"
    )
    print()
    print("     # Example: run while searching for a specific search term")
    print(
        "     docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest heimdall"
    )
    print()


def main(argv) -> None:
    """Main execution to setup the Viewer."""

    viewer: k8v.viewer.Viewer = k8v.viewer.Viewer()
    try:
        opts, args = getopt.getopt(
            argv,
            "Avhc:f:e:i:n:o:r:s:",
            [
                "colors",
                "all-namespaces",
                "exclude",
                "filter",
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
