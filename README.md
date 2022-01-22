# k8v (Kubernetes Viewer)

k8v is a command line utility used to view information about a Kubernetes cluster. It allows the user to view 
multiple resources at once, optionally in a hierarchy, as well as provide filtering capabilities.

Note: this tool is not intended as a replacement for *kubectl* and is only intended to provide more flexible 
visibility into a Kubernetes cluster.



## Filtering capabilities

This tool provides a number of ways to search for specific resources and filter them as desired. This includes 
the ability to search for resources across all namespaces, or a list of specified namespaces, match labels that
are specified for selectors, or simple search the *name* of the resource for a specific string that should be
included in the results.

Filtering strings for a *name* can be specified using the -i | --include option or simply passing arguments
on the command line after you specifiy all other options:

    # search all namespaces for resources that have *heimdall* in their name
    $ bin/k8v -A -o brief -i heimdall
    service/default/heimdall
    ingress/default/heimdall
    deployment/default/heimdall
    pod/default/heimdall-9864f4f59-8m5ls
    persistentvolumeclaim/default/heimdall

    # this is equivalent to the example above (note: the search criteria is specifed after all other options)
    $ bin/k8v -A -o brief heimdall
    service/default/heimdall
    ingress/default/heimdall
    deployment/default/heimdall
    pod/default/heimdall-9864f4f59-8m5ls
    persistentvolumeclaim/default/heimdall


Specific matches can also be excluded from the matched results using the -e | --exclude option:

    # search all namespaces for resources that have *heimdall* in their name
    $ bin/k8v -A -o brief -i heimdall -e 9864f4f59-8m5ls
    service/default/heimdall
    ingress/default/heimdall
    deployment/default/heimdall
    persistentvolumeclaim/default/heimdall


## Resource types

The tool is able to specify a list of supported resource types that should be searched, or will default to a 
specific set if not requested at runtime. These are the resources types currently included by default:

  * ConfigMap
  * Secret
  * Services
  * Ingress
  * Deployment
  * DaemonSet
  * ReplicaSet
  * StatefulSet
  * Pods
  * PersistentVolume (only displayed when using -A | --all-namespaces option)
  * PersistentVolumeClaim

If you want a specific set of resource types to search you can do that using the -r | --resource option.
These resources will be displayed in the order they are requested on the command line:

    # show all services and ingresses in the default namespace with names matching "heimdall" in a specific order
    $ bin/k8v -r service -r ingress heimdall
    service/default/heimdall (type=LoadBalancer cluster_ip=10.43.39.132  ports=[80:80/TCP nodeport=30242443:443/TCP nodeport=32661])
    ingress/default/heimdall (host=dashboard.k.hazil.net [/=heimdall:80] )



## Output formats

A variety of output formats are supported by the tool. 

The following output types are supported:
* brief - one line per matched resource
* default - one line per resource including details, as well as related resources one line per resource with details
* full - one line per resource including details, as well as ALL related resources one line per resource with details
* json - a JSON formatted list of matching resources that can be processed by other tools that can parse JSON



### Default output

The default output will show each resource with one line per resource that includes useful information about
that resource. If the *-a* or *--all-related* parameter is specified then each related resource will show up with
indentation to represent a relationship between them.

This allows you to see a lot of information in a hierarchy quickly with filtering capabilities as needed.

    # list all resources matching *heimdall* using the default view
    $ bin/k8v -a heimdall
    service/default/heimdall (type=LoadBalancer cluster_ip=10.43.39.132  ports=[80:80/TCP nodeport=30242:443/TCP])
    ingress/default/heimdall (host=heimdall.example.com [/=heimdall:80])
    deployment/default/heimdall (labels=[app=heimdall] replicas=1/1 (upd=1 avail=1) strategy=Recreate generation=14)
            replicaset/default/heimdall-9864f4f59 (labels=[app=heimdall pod-template-hash=9864f4f59] replicas=1/1 (avail=1) generation=3)
                    pod/default/heimdall-9864f4f59-8m5ls (labels=[app=heimdall pod-template-hash=9864f4f59] sa=default config_maps= secrets= pvc=heimdall)
    pod/default/heimdall-9864f4f59-8m5ls (labels=[app=heimdall pod-template-hash=9864f4f59] sa=default config_maps= secrets= pvc=heimdall)
    persistentvolumeclaim/default/heimdall (storage_class=nfs-client access_modes=['ReadWriteMany'] capacity=1Gi volume=pvc-8c5af527-cd3f-4a37-88fa-89d0d7523c81 phase=Bound)



### Brief output

The brief output will simply list each of the matching resources one per line and can be used to quickly find
a set of resources that match some specific criteria (namespace, search query, excluded query, etc.).

This output is generated in such a way that it can be used to drive scripted or automated processes and will 
only report individual resources that match the input search criteria and nothing else. 

    # list each default resource in the *metallb* namespace
    $ bin/k8v -n metallb -o brief
    configmap/metallb/kube-root-ca.crt
    configmap/metallb/metallb
    secret/metallb/default-token-cbsxv
    secret/metallb/metallb-controller-token-jfqhf
    secret/metallb/metallb-memberlist
    secret/metallb/metallb-speaker-token-rnqh9
    secret/metallb/sh.helm.release.v1.metallb.v1
    daemonset/metallb/metallb-speaker
    deployment/metallb/metallb-controller
    pod/metallb/metallb-controller-7cb7dd579d-zvcts
    pod/metallb/metallb-speaker-ffwcc
    pod/metallb/metallb-speaker-hgvpd
    pod/metallb/metallb-speaker-r9kv6
    pod/metallb/metallb-speaker-s6ps5
    pod/metallb/metallb-speaker-vmpcr
    pod/metallb/metallb-speaker-zxr8l


Note: if you are including all related resources you may need to deal with whitespace or parse accordingly if
using another tool to process the output:

    $ bin/k8v -c default -i heimdall -a -o brief
    service/default/heimdall
    ingress/default/heimdall
    deployment/default/heimdall
        replicaset/default/heimdall-9864f4f59
            pod/default/heimdall-9864f4f59-8m5ls
    pod/default/heimdall-9864f4f59-8m5ls
    persistentvolumeclaim/default/heimdall



### Full output

The full output is currently the same as the default view but will show more detailed *related* resources 
visually indented below the resource instead of summarizing them.

This will includes many resource types such as ConfigMap, Ingress, NetworkPolicy, Secret, Service, etc. 
that are currently only summarized for the parent resource.



### JSON output

The JSON output will generate a valid JSON list containing each matching resources within the list. This 
output can then be used by various tools that understand the JSON format.


    # example using jq utility to parse generated output
    $ bin/k8v -c default -a -i heimdall -o json | jq '.[0].spec'
    {
    "cluster_i_ps": [
        "10.43.39.132"
    ],
    "cluster_ip": "10.43.39.132",
    "external_traffic_policy": "Cluster",
    "ip_families": [
        "IPv4"
    ],
    "ip_family_policy": "SingleStack",
    "local_vars_configuration": "",
    "ports": [
        {
        "local_vars_configuration": "",
        "name": "http",
        "node_port": 30242,
        "port": 80,
        "protocol": "TCP",
        "target_port": 80
        },
        {
        "local_vars_configuration": "",
        "name": "https",
        "node_port": 32661,
        "port": 443,
        "protocol": "TCP",
        "target_port": 443
        }
    ],
    "selector": {
        "app": "heimdall"
    },
    "session_affinity": "None",
    "type": "LoadBalancer"
    }



## Setup using Python

In order to run the tool directly you need to clone the repository and install the dependencies:

    # clone the repository and navigate to the project folder
    git clone git@github.com:jasonhanks/k8v.git
    cd k8v
    
    # optional: setup virtualenv for the project (recommended)
    python3 -mvenv .env
    source .env/bin/activate

    # install the dependencies
    pip3 install -r requirements.txt



## Kubernetes configuration

By default the tool reads the *KUBECONFIG* environment variable for the location of the configuration to use, or
will default to *~/.kube/config* otherwise.



## Usage with Python

Here are a few various examples of how to use the utility:

    # view the usage for the tool using specified KUBECONFIG file
    KUBECONFIG=/etc/rancher/k3s/k3s.yaml bin/k8v

    # view *brief* listing of all default resources for all namespaces
    bin/k8v -A -o brief
    
    # view all *services* and *ingress* resources in the specified namespace
    bin/k8v -n heimdall -r ingress -r service

    # view all default resources matching the specififed search query
    bin/k8v nginx



## ANSI color schemes

Basic ANSI support has been added and schemes can be configured by editing the k8s/color-schemes.json file. 
Multiple schemes are supported and non-default schemes can be specified at runtime using the *-c* or 
*--colors* option.

By default all ANSI color schemes are *disabled*. In order to enable them try passing **-c default** or **--colors default** as a parameter to the utility.


# Docker Container

This project maintains a publicly availble container image on the Docker Hub. The official container for
the latest version is: jasonhanks/k8s:latest

## Kubernetes configuration

In order to specify the Kubernetes configuration with the Docker container you must pass it a volume 
with the desired cluster configuration overriding /app/.kube/config inside the container. 

See the Usage section for examples.


## Usage

Here are a few various examples of how to use the container to run the utility:

    # view the usage for the tool using specified KUBECONFIG file
    docker run -it --rm -v /etc/rancher/k3s/k3s.yaml:/app/.kube/config jasonhanks/k8v:latest

    # view *brief* listing of all default resources all namespaces
    docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -A -o brief

    # view all *services* and *ingress* resources in the specified namespace
    docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -n heimdall -r ingress -r service

    # view all default resources matching the specififed search query
    docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest nginx
