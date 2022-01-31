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

    # search all namespaces for resources that have *nginx* in their name
    $ k8v -A -o brief -i nginx
    configmap/default/nginx-cm
    deployment/default/nginx-deployment
    persistentvolumeclaim/default/nginx-pvc
    pod/default/nginx-deployment-7b6fcd488c-5zm67
    pod/default/nginx-deployment-7b6fcd488c-j9tkn
    replicaset/default/nginx-deployment-7b6fcd488c
    secret/default/nginx-sec
    service/default/nginx

    # this is equivalent to the example above (note: the options have changed, no -i required for inclusive 
    # searches of last argument)
    $ k8v -A -ob nginx
    configmap/default/nginx-cm
    deployment/default/nginx-deployment
    persistentvolumeclaim/default/nginx-pvc
    pod/default/nginx-deployment-7b6fcd488c-5zm67
    pod/default/nginx-deployment-7b6fcd488c-j9tkn
    replicaset/default/nginx-deployment-7b6fcd488c
    secret/default/nginx-sec
    service/default/nginx


Resources can also be excluded from the matched results using the -e | --exclude option:

    # search all namespaces for resources that have *nginx* 
    $ k8v -A -ob -i nginx
    configmap/default/nginx-cm
    deployment/default/nginx-deployment
    persistentvolumeclaim/default/nginx-pvc
    pod/default/nginx-deployment-7b6fcd488c-5zm67
    pod/default/nginx-deployment-7b6fcd488c-j9tkn
    replicaset/default/nginx-deployment-7b6fcd488c
    secret/default/nginx-sec


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

If you want a specific set of resource types to search you can do that using the -r | --resource option (multiple
-r options are supported for various resource types).

    # show all services in the default namespace with names matching "nginx"
    $ k8v -r service -r deployment nginx
    service/default/nginx (type=ClusterIP cluster_ip=10.96.134.184 ports=[80=80/TCP ])
    deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)


## Output formats

A variety of output formats are supported by the tool. 

The following output types are supported:
* *brief* - one line per matched resource
* *default* - one line per resource including informative details (default)
* *json* - a JSON formatted list of matching resources that can be processed by other tools that can parse JSON
* *pickle* - a binary format containing a list of matching resources common in Python


### Default format

The default format will show each resource with one line per resource that includes useful information about
that resource. 

If the *-t* or *--related* parameter is specified then each related resource will show up with
indentation to represent a relationship between them. This allows you to see a lot of information in a hierarchy quickly with filtering capabilities as needed.

    # list all resources matching *nginx* using the default view
    $ k8v -t nginx
    configmap/default/nginx-cm (data=[ENV, app])
    deployment/default/nginx-deployment (labels=[app=nginx] replicas=2/2 upd=2 avail=2 strategy=RollingUpdate max_surge=25% max_unavailable=25% generation=1)
            replicaset/default/nginx-deployment-7b6fcd488c (labels=[app=nginx pod-template-hash=7b6fcd488c] replicas=2/2 avail=2 generation=1)
                    pod/default/nginx-deployment-7b6fcd488c-5zm67 (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
                    pod/default/nginx-deployment-7b6fcd488c-j9tkn (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
    persistentvolumeclaim/default/nginx-pvc (access_modes=standard storage_class=['ReadWriteOnce'] capacity=32Mi volume=pvc-21b34ba7-7311-49cb-b84a-b00ff1b17943 phase=Bound)
    pod/default/nginx-deployment-7b6fcd488c-5zm67 (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
    pod/default/nginx-deployment-7b6fcd488c-j9tkn (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
    replicaset/default/nginx-deployment-7b6fcd488c (labels=[app=nginx pod-template-hash=7b6fcd488c] replicas=2/2 avail=2 generation=1)
            pod/default/nginx-deployment-7b6fcd488c-5zm67 (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
            pod/default/nginx-deployment-7b6fcd488c-j9tkn (labels=[app=nginx pod-template-hash=7b6fcd488c] sa=default configmaps=[['nginx-cm']] pvcs=[['nginx-pvc']])
    secret/default/nginx-sec (data=[PASSWORD, USERNAME])
    service/default/nginx (type=ClusterIP cluster_ip=10.96.134.184 ports=[80=80/TCP ])



### Brief format

The brief format will simply list each of the matching resources one per line and can be used to quickly find
a set of resources that match some specific criteria (namespace, search query, excluded query, etc.).

This format is generated in such a way that it can be used to drive scripted or automated processes and will 
only report individual resources that match the input search criteria and nothing else. 

    # list each default resource in the *metallb* namespace
    $ k8v -ob nginx
    configmap/default/nginx-cm
    deployment/default/nginx-deployment
    persistentvolumeclaim/default/nginx-pvc
    pod/default/nginx-deployment-7b6fcd488c-5zm67
    pod/default/nginx-deployment-7b6fcd488c-j9tkn
    replicaset/default/nginx-deployment-7b6fcd488c
    secret/default/nginx-sec
    service/default/nginx


Note: if you are including all related resources (-t | --related) you may need to deal with whitespace or parse 
accordingly if using another tool to process the output:

    $ k8v -c default -t -ob -inginx
    configmap/default/nginx-cm
    deployment/default/nginx-deployment
            replicaset/default/nginx-deployment-7b6fcd488c
                    pod/default/nginx-deployment-7b6fcd488c-5zm67
                    pod/default/nginx-deployment-7b6fcd488c-j9tkn
    persistentvolumeclaim/default/nginx-pvc
    pod/default/nginx-deployment-7b6fcd488c-5zm67
    pod/default/nginx-deployment-7b6fcd488c-j9tkn
    replicaset/default/nginx-deployment-7b6fcd488c
            pod/default/nginx-deployment-7b6fcd488c-5zm67
            pod/default/nginx-deployment-7b6fcd488c-j9tkn
    secret/default/nginx-sec
    service/default/nginx


### JSON format

The JSON format will generate a valid JSON list containing each matching resources within the list. This 
output can then be used by various tools that understand the JSON format (such as *jq* shown below).

    # example using jq utility to parse generated output
    $ k8v -ojson nginx | jq '.[].metadata.name'
    "nginx-cm"
    "nginx-deployment"
    "nginx-pvc"
    "nginx-deployment-7b6fcd488c-5zm67"
    "nginx-deployment-7b6fcd488c-j9tkn"
    "nginx-deployment-7b6fcd488c"
    "nginx-sec"
    "nginx"


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
    k8v -n nginx -r pod -r service

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

    # view all *services* and *pod* resources in the specified namespace
    docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -n nginx -r pod -r service

    # view all default resources matching the specififed search query
    docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest nginx
