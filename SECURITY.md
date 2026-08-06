# Security Policy

## Supported versions

Security fixes are applied only to the latest released version on the
`main` branch (and the matching release of `ansible-base`).

| Version | Supported |
| --- | --- |
| latest release | ✅ |
| older releases | ❌ |

## Reporting a vulnerability

**Please do not open a public issue.** GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
is the preferred channel:

1. Go to the repository's **Security** tab.
2. Click **Report a vulnerability**.
3. Describe the issue with reproduction steps and a suggested mitigation.

If you cannot use GitHub's form, email **goabonga@pm.me** with the same
information. PGP encryption is available on request.

You can expect an acknowledgement within **3 business days**, a triage
assessment within **10 business days**, and a fix or written mitigation
plan before any public disclosure.

## Scope

`ansible-base` provisions a **local, throwaway** lab: KVM guests on an
isolated NAT network, reachable only from the workstation that created them.
The defaults shipped in `inventory/group_vars/` are deliberately permissive
for that setting.

In scope, and worth reporting:

- the roles weakening the guests beyond what the lab requires — file modes,
  service hardening, sudo rules, secret generation and storage;
- a template or task that leaks a secret into logs, into a world-readable
  file, or into the repository;
- artefacts installed without checksum verification, or from an unexpected
  source;
- anything that exposes the guests, or the workstation, outside the lab
  network.

Out of scope: the permissive lab defaults themselves, the absence of TLS
inside the lab network, and vulnerabilities in the software a downstream
project chooses to deploy on the guests — report those upstream.

Thanks for helping keep the project and its users safe.
