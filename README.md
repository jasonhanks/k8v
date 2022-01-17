# k8v (Kubernetes Viewer)

k8v is a command line utility used to view information about a Kubernetes cluster. It allows the user to view 
multiple resources at once, optionally in a hierarchy, as well as provide filtering capabilities.

Note: this tool is not intended as a replacement for *kubectl* and is only intended to provide more flexible 
visibility into a Kubernetes cluster.



## Setup using Python

In order to run the tool directly you need to clone the repository and install the dependencies:

    # default environment
    pip install -r requirements.txt

    # alternatively using virtualenv
    python3 -mvenv .env
    source .env/bin/activate
    pip install -r requirements.txt



## Kubernetes configuration

By default the tool reads the *KUBECONFIG* environment variable for the location of the configuration to use, or
will default to *~/.kube/config* otherwise.



## Usage with Python

Here are a few various examples of how to use the utility:

    # view the usage for the tool using specified KUBECONFIG file
    KUBECONFIG=/etc/rancher/k3s/k3s.yaml python3 k3s/k3s.py

    # view *brief* listing of all deafult resources all namespaces
    python3 k8v/k8v.py -A -d brief
    
    # view all *services* and *ingress* resources in the specified namespace
    python3 k8v/k8v.py -n heimdall -r ingress -r service

    # view all default resources matching the specififed search query
    python3 k8v/k8v.py nginx



## Sample output

This section includes some sample output from the different views to get an idea of what
the output looks like.



### Brief view

The brief view will simply list each of the matching resources one per line.

    # list each default resource in the *metallb* namespace
    $ python3 k8v/k8v.py -n metallb -d brief
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


### Default view

The default view will show each resource with one line per resource that includes various information about
those resources. Additionally some resources will also display related resources on a separate
line including their own details with indention to visually see the relationships.

This allows the user to see a low of information quickly by using various filtering capabilities.

    # list all resources matching *heimdall* using the default view
    $ python3 k8v/k8v.py heimdall
    service/default/heimdall (type=LoadBalancer cluster_ip=10.43.39.132  ports=[80:80/TCP nodeport=30242443:443/TCP nodeport=32661])
    ingress/default/heimdall (host=heimdall.example.com (/ => heimdall:80) )
    deployment/default/heimdall (labels=[app=heimdall] replicas=1/1 (upd=1 avail=1) strategy=Recreate generation=14)
            replicaset/default/heimdall-9864f4f59 (labels=[app=heimdall pod-template-hash=9864f4f59] replicas=1/1 (avail=1) generation=3)
                    pod/default/heimdall-9864f4f59-8m5ls (labels=[app=heimdall pod-template-hash=9864f4f59] sa=default config_maps= secrets= pvc=heimdall)
    pod/default/heimdall-9864f4f59-8m5ls (labels=[app=heimdall pod-template-hash=9864f4f59] sa=default config_maps= secrets= pvc=heimdall)


Note: this view will eventually have ANSI color support to make it more visually appealing.


### Full view

The full view is currently the same as the default view but will eventually show more *children* resources instead of 
simply summarizing them.



# Docker Container

This project maintains a publicly availble container image on the Docker Hub. 



## Kubernetes configuration

In order to specify the Kubernetes configuration with the Docker container you must pass it a volume 
with the desired cluster configuration overriding /app/.kube/config inside the container. 

See the Usage section for examples.


## Usage

Here are a few various examples of how to use the container to run the utility:

    # view the usage for the tool using specified KUBECONFIG file
    docker run -it --rm -v /etc/rancher/k3s/k3s.yaml:/app/.kube/config jasonhanks/k8v:latest

    # view *brief* listing of all deafult resources all namespaces
    docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -A -d brief

    # view all *services* and *ingress* resources in the specified namespace
    docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest -n heimdall -r ingress -r service

    # view all default resources matching the specififed search query
    docker run -it --rm -v ~/.kube:/app/.kube jasonhanks/k8v:latest nginx
