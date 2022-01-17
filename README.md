# k8v (Kubernetes Viewer)

k8v is a command line utility used to view various information about a Kubernetes cluster at a glance. 

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

By default the tool reads the *KUBECONFIG* environment variable for the location of the configuratio to use, or
will default to *~/.kube/config* otherwise.



## Usage with Python

Here are a few various examples of how to use the utility:

    # view the usage for the tool using specified KUBECONFIG file
    KUBECONFIG=/etc/rancher/k3s/k3s.yaml python3 k3s/k3s.py

    # view *brief* listing of all deafult resources all namespaces
    python3 k3s/k3s.py -A -d brief
    
    # view all *services* and *ingress* resources in the specified namespace
    python3 k3s/k3s.py -n heimdall -r ingress -r service

    # view all default resources matching the specififed search query
    python3 k3s/k3s.py nginx



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
