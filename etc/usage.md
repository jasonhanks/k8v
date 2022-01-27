
NAME
        k8v - view Kubernetes cluster resources

SYNOPSIS
        k8v [OPTION]... [QUERY]...

DESCRIPTION
        This utility is used to quickly see a lot of information about a Kubernetes context (default namespace is: default). This will display all the desired 
        resources by type (default: configmap, deployments, daemonsets, ingresses, persistentvolume, persistentvolumeclaim, replicasets, pods, secrets, 
        services, and statefulset) and display various information about them.

        Filtering capabilities are provided which can either exclude or include matching resources as needed. By default any arguments that are not available 
        options below will be used as search criteria (same behavior as --include option).

        -c, --colors=SCHEME
                colorize the output; SCHEME can be 'default' (default if omitted), or 'none' for no color output

        -o, --output=TYPE
                output mode used to display matching resources; TYPE can be 'wide' (default if omitted), 'brief' for list of resource, or 'json' for full information

        -f, --file
                specify a filename to be used for output (STDOUT if omitted)

        -A, --all-namespaces
                search for matching resources that exist in all namespaces

        -n, --namespace=NAMESPACE
                search for resources in the specified namespace; NAMESPACE can be any valid namespace ('default' if omitted); can be specified more than once

        -R, --all-resources
                search for matching resources with any supported type

        -r, --resource=TYPE
                search for matching resources with the specified type; can be specified more than once

        -e, --exclude=QUERY
                exclude any matching resources who's name includes the specified QUERY; can be specified more than once

        -i, --include=QUERY
                include any matching resources who's name includes the specified QUERY; can be specified more than once

        -s, --selector=SELECTOR
                include any matching resources who have a matching label matching the SELECTOR (e.g. LABEL=value); can be specified more than once

         -t, --all-related
                display related resources in a hierachy structure

        -v, --verbose
                display verbose logging messages

KUBERNETES:
        By default k8v uses the KUBECONFIG environment variable for the Kubernetes cluster configuration. If not specified it will default to ~/.kube/config.

DOCKER
        Docker users will need to use the following syntax to pass their Kubernetes configuration as well as other command line arguments, otherwise the 
        container will only display this message.

        # Example: run with default view
        docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest --

        # Example: run with brief view for a specific namespace
        docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -o brief -n metallb

        # Example: run while searching for a specific search term
        docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest heimdall

    Exit status:
        0      if OK,
        1      if problems are encountered (e.g., cannot connect to Kubernetes cluster, cannot locate color scheme, etc.)

AUTHOR:
        Written by Jason Hanks.

REPORTING BUGS:
        GitHub Project: https://github.com/jasonhanks/k8v.

LICENSE:
        This project is distributed under an MIT License. See included LICENSE file for details.

