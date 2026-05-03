---
sidebar_position: 7
---

# K3s Setup

## About K3s Kubernetes Cluster:

Setting up a production-ready kubernetes cluster with k3s is a fairly easy process with minimal setup efforts.

Since k3s is a light-weight kubernetes cluster, it is chosen for this setup with 2GB of RAM on each nodes. 

The reference architecture of the k3s Kubernetes cluster can be found here: [Architecture](https://docs.k3s.io/architecture).

By default, k3s clusters are deployed with an Ingress Controller called Traefik and a Load Balancer with svc-lb as the IP provider of the Load Balancer. This makes K3s super useful in quick setup.

Thus K3s has the following dependencies already pre-shipped with it:

- containerd / cri-dockerd container runtime (CRI)
- Flannel Container Network Interface (CNI)
- CoreDNS Cluster DNS
- Traefik Ingress controller
- ServiceLB Load-Balancer controller
- Kube-router Network Policy controller
- Local-path-provisioner Persistent Volume controller
- Spegel distributed container image registry mirror
- Host utilities (iptables, socat, etc)


## K3S Installation

1. For installing k3s, if the debian machine is used for k3s server (deb-k3s-master) node, then run:

```bash
curl -sfL https://get.k3s.io | sh -s - server --cluster-cidr=10.244.0.0/16 --service-cidr=10.96.0.0/16 --write-kubeconfig-mode 644 --disable=traefik
```

2. Fetch master token:

```bash
sudo cat /var/lib/rancher/k3s/server/node-token
```

3. For installing k3s agent on debian agent (deb-k3s-agent) node (as well as for raspberry pi):

```bash
curl -sfL https://get.k3s.io | K3S_URL=https://192.168.0.202:6443 K3S_TOKEN=< k3s-server-token > sh -s -
```

## Configure kubectl

For accessing and managing the cluster resources using kubectl from personal laptop or another machine outside of the k3s cluster:

1. Copy and paste kubeconfig file from k3s master node and save it in a seperate file - say my-config.yaml. The kubeconfig file in the k3s server can be found in ```/etc/rancher/k3s/k3s.yaml```.

2. Just overwrite /.kube/config:

```bash
mkdir -p ~/.kube
cp my-config.yaml ~/.kube/config
```

## Install Helm

To install helm:
1. Run the following commands:
```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

2. Verify installation:
```bash
helm version
```