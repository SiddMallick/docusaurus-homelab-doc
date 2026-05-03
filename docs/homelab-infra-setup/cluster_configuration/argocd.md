---
sidebar_position: 12
---

# ArgoCD

# ArgoCD Image updater:

To install argocd image updater:

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/v0.12.2/manifests/install.yaml
```

Watch the logs immediately after installation:

```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater -f
```