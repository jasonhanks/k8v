FROM python:3.10.1-slim


# Create the k8v user
RUN useradd -m -d /app k8v


# Switch to the k8v user
USER k8v


# Use the home directory for the app
WORKDIR /app


# Create directory for Kubeconfig file / volume mappings
RUN mkdir /app/.kube


# Install Python pip based dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


# Copy the project files to the /app directory
COPY . .


# Execute the utility and display the usage by default
ENTRYPOINT [ "bin/k8v"]
CMD ["-h"]
