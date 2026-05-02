---
sidebar_position: 8
---

# Cloudflare Domain

A domain without A Records is required to sign certificates using cert-manager and Let's Encrypt.

1. The domain siddhomelab.cc is registered with Cloudflare.
2. Next, generate an API key in Cloudflare for cert-manager to configure the Cluster-Issuer.
3. This API Token needs to be stored in tfvars file in local for terraform kubernetes setup.