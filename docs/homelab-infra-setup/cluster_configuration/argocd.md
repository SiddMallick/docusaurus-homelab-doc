---
sidebar_position: 12
---

# ArgoCD

The terraform code in homelab-k3s repo already installs ArgoCD through helm using terraform.

# ArgoCD Image updater:

To install argocd image updater:

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/v0.12.2/manifests/install.yaml
```

Watch the logs immediately after installation:

```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater -f
```