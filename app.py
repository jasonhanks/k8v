import getopt
import io
import sys

import k8v


def usage(output: io.IOBase) -> None:
    """Display the command line usage help screen."""

    with open("etc/usage.md") as f:
        for line in f.readlines():
            output.write(line)
        f.close()


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
        usage(viewer.config.file)
        print(f"ERROR: {e}")
        print()
        sys.exit(2)

    for opt, arg in opts:
        # display the help
        if opt in ("-h", "--help"):
            usage(viewer.config.file)
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
