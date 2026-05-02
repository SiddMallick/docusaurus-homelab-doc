---
sidebar_position: 11
---

# SSL/TLS Certificates with Cert Manager

To enable HTTPS connection between the hosted applications and the client (browser), we will need to create, manage and renew certificates for the HTTP connections. This can easily be done using cert-manager, let's encrypt and dns-01 challenge.

## What is cert-manager?

cert-manager creates TLS certificates for workloads in your Kubernetes or OpenShift cluster and renews the certificates before they expire.

cert-manager can obtain certificates from a variety of certificate authorities, including: Let's Encrypt, HashiCorp Vault, CyberArk Certificate Manager and private PKI.

Here, we'll use cert-manager with Let's Encrypt and obtain signed certificates using the DNS-01 challenge

## Install cert-manager

1. First create a custom-values.yaml file:

```yaml
# custom-values.yaml
crds:
  enabled: true
replicaCount: 2
extraArgs:
  - --dns01-recursive-nameservers=8.8.8.8:53 # Set DNS IP in which your DNS record points to a TXT record
  - --dns01-recursive-nameservers-only
podDnsPolicy: None
podDnsConfig:
  nameservers:
    - "8.8.8.8"
```

2. Install cert-manager using helm chart:

```bash
helm install \
  cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --version v1.20.2 \
  --namespace cert-manager \
  --create-namespace \
  -f custom-values.yaml
```

3. Verify installation:

```bash
kubectl get all -n cert-manager
```

## Create Cloudflare API token secret

For creating a certificate issuer so that it can issue valid SSL certificates on your behalf, you need to first get the API token of Cloudflare from Cloudflare Dashboard and store it as a kubernetes secret.

To generate an API token from Cloudflare Dashboard:

1. Login to your cloudflare dashboard account
2. Click on the profile icon
3. Click on API Tokens
4. Click on Create API Token -> Create Custom Token
5. Provide a name to the API token for reference
6. Add two permissions:

| Level | Sub-Level | Permission |
|------|------|-----------|
| Zone | Zone | Read-Only |
| Zone | DNS | Edit |

7. Include only your zone in Zone Resources. Select Include -> Specific Zone -> your-domain (siddhomelab.cc)
8. Create the API token and copy it
9. Run the following command to create a secret in kubernetes to store the api-token securely inside the cluster:

```bash
kubectl create secret generic cloudflare-api-token-secret \
  --from-literal=api-token=YOUR_API_TOKEN \
  -n cert-manager
```

## Create Cluster Issuer

Next, you will need to create a ClusterIssuer which will issue SSL/TLS certificate to Let's Encrypt (Or any CA of your choice).

Selecting the cloudflare domain as siddhomelab.cc, the YAML file for ClusterIssuer looks like:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-cloudflare
spec:
  acme:
    email: <your-email-address>
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - dns01:
        cloudflare:
          email: <your-email-address=cloudflare>
          apiTokenSecretRef:
            name: cloudflare-api-token-secret # <- This secret was created above
            key: api-token
      selector:
        dnsZones:
          - "siddhomelab.cc"
```

Apply and check whether letsencrypt-cloudflare Cluster Issuer is created or not by running ```kubectl get clusterissuer```.

## Create Certificates

Since the homelab apps will be in seperate namespaces with Ingresses created in the specific namespaces, we need to create multiple certificates per namespace.

:::tips[Using Gateway API]
If you are using a Gateway API, you can deploy the Gateway object which will terminate the TLS and thus only one SSL/TLS cert needs to be created / maintained for all the hosted applications.
:::

```certificate.yaml``` for this docusaurus homelab docs was created like this :

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: local-sidd-cc-homelab-docs
  namespace: docs
spec:
  secretName: local-sidd-cc-tls-homelab-docs
  issuerRef:
    name: letsencrypt-cloudflare
    kind: ClusterIssuer
  commonName: "*.siddhomelab.cc"
  dnsNames:
  - "siddhomelab.cc"
  - "*.siddhomelab.cc" # wildcard represents that any hosts like homepage.siddhomelab.cc or grafana.siddhomelab.cc

```

Apply the above yaml and run the command:

```bash
watch kubectl get challenges -n < namespace >
```

You will see that the challenges are in a Pending state. Once all the challenges are completed, your cert will be in a true state and the challenges will immediately dissapper. This means that the specific certificate can be used for tls termination in ingress configuration of individual application. Note that the above uses a dns-01 challenge as it was mentioned in the installation helm values.yaml file.