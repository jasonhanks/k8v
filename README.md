# k8v

k8v is a command line utility used to view resources in a Kubernetes cluster. It allows the user to view 
multiple resources at once, optionally in a related hierarchy, as well as provide advanced filtering capabilities.

Note: this tool is not intended as a replacement for *kubectl* and is only intended to provide more flexible 
visibility into a Kubernetes cluster. It will not make changes to a Kubernetes cluster.



## Filtering capabilities

This tool provides a number of ways to search for resources and filter the results. This includes the ability to 
search for resources across all namespaces, or a list of namespaces, match label selectors, or search by *name* 
for resources that should be included or excluded in the results.

Filtering strings for a *name* can be specified using the -i | --include option or simply passing arguments
on the command line after you specifiy all other options:

    # search all namespaces for resources that have *heimdall* in their name
    $ k8v -A -o brief -i heimdall
    service/default/heimdall
    ingress/default/heimdall
    deployment/default/heimdall
    pod/default/heimdall-9864f4f59-8m5ls
    persistentvolumeclaim/default/heimdall

    # this is equivalent to the example above (note: the search criteria is specifed after all other options)
    $ k8v -A -ob heimdall
    service/default/heimdall
    ingress/default/heimdall
    deployment/default/heimdall
    pod/default/heimdall-9864f4f59-8m5ls
    persistentvolumeclaim/default/heimdall


Resources can also be excluded from the matched results using the -e | --exclude option:

    # search all namespaces for resources that have *heimdall* in their name but exclude those with *9864f4f59-8m5ls* in their name
    $ k8v -A -o brief -i heimdall -e 9864f4f59-8m5ls
    service/default/heimdall
    ingress/default/heimdall
    deployment/default/heimdall
    persistentvolumeclaim/default/heimdall


## Resource types

The tool is able to require a list of supported resource types that should be searched, or will default to the 
following types otherwise (see: ResourceType):

  * ConfigMap
  * CronJobs
  * DaemonSets
  * Deployment
  * Ingress
  * Jobs
  * PersistentVolume
  * PersistentVolumeClaim
  * Pods
  * ReplicaSet
  * Secret
  * Services
  * StatefulSet

If you want a specific set of resource types to search you can do that using the -r | --resource option.
These resources will be displayed in the order they are requested on the command line:

    # show all services and ingresses in the default namespace with names matching "heimdall" in a specific order
    $ k8v -r service -r ingress heimdall
    service/default/heimdall (type=LoadBalancer cluster_ip=10.43.39.132  ports=[80:80/TCP nodeport=30242443:443/TCP nodeport=32661])
    ingress/default/heimdall (host=dashboard.k.hazil.net [/=heimdall:80] )



## Output formats

A variety of output formats are supported by the tool. 

The following output types are supported:
* *brief* - one line per matched resource
* *wide* - one line per resource including informative details
* *json* - a JSON formatted list of matching resources that can be processed by other tools that can parse JSON
* *pickle* - a binary format containing a list of matching resources common in Python


### Default format

The default format will show each resource with one line per resource that includes useful information about
that resource. If the *-t* or *--related* parameter is specified then each related resource will show up with
indentation to represent a relationship between them.

This allows you to see a lot of information in a hierarchy quickly with filtering capabilities as needed.

    # list all resources matching *heimdall* using the default view
    $ k8v -t heimdall
    service/default/heimdall (type=LoadBalancer cluster_ip=10.43.39.132  ports=[80:80/TCP nodeport=30242:443/TCP])
    ingress/default/heimdall (host=heimdall.example.com [/=heimdall:80])
    deployment/default/heimdall (labels=[app=heimdall] replicas=1/1 (upd=1 avail=1) strategy=Recreate generation=14)
            replicaset/default/heimdall-9864f4f59 (labels=[app=heimdall pod-template-hash=9864f4f59] replicas=1/1 (avail=1) generation=3)
                    pod/default/heimdall-9864f4f59-8m5ls (labels=[app=heimdall pod-template-hash=9864f4f59] sa=default config_maps= secrets= pvc=heimdall)
    pod/default/heimdall-9864f4f59-8m5ls (labels=[app=heimdall pod-template-hash=9864f4f59] sa=default config_maps= secrets= pvc=heimdall)
    persistentvolumeclaim/default/heimdall (storage_class=nfs-client access_modes=['ReadWriteMany'] capacity=1Gi volume=pvc-8c5af527-cd3f-4a37-88fa-89d0d7523c81 phase=Bound)



### Brief format

The brief format will simply list each of the matching resources one per line and can be used to quickly find
a set of resources that match some specific criteria (namespace, search query, excluded query, etc.).

This format is generated in such a way that it can be used to drive scripted or automated processes and will 
only report individual resources that match the input search criteria and nothing else. 

    # list each default resource in the *metallb* namespace
    $ k8v -n metallb -o brief
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

    $ k8v -c default -i heimdall -t -o brief
    service/default/heimdall
    ingress/default/heimdall
    deployment/default/heimdall
        replicaset/default/heimdall-9864f4f59
            pod/default/heimdall-9864f4f59-8m5ls
    pod/default/heimdall-9864f4f59-8m5ls
    persistentvolumeclaim/default/heimdall


### JSON format

The JSON format will generate a valid JSON list containing each matching resources within the list. This 
output can then be used by various tools that understand the JSON format (such as *jq* shown below).


    # example using jq utility to parse generated output
    $ bin/k8v -c default -t -i heimdall -o json | jq '.[0].spec'
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



### Pickle format

The Pickle format is a binary serialization format commonly used in Python programs to read or write objects
to files. This currently used for serializing test data for the automated tests.

For more information see: https://docs.python.org/3/library/pickle.html



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

    # view the default resources using the specified KUBECONFIG file
    KUBECONFIG=/etc/rancher/k3s/k3s.yaml k8v

    # view *brief* listing of all default resource types in all namespaces
    k8v -A -o brief
    
    # view all *services* and *ingress* resources in the specified namespace
    k8v -n heimdall -r ingress -r service

    # view all default resources matching the specififed search query
    k8v nginx



## ANSI color schemes

Basic ANSI support has been added and schemes can be configured by editing the k8s/color-schemes.json file. 
Multiple schemes are supported and non-default schemes can be specified at runtime using the *-c* or 
*--colors* option.

By default the ANSI color schemes are *enabled*. In order to disable ANSI output specify the **-c none** or **-cnone** option.


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
