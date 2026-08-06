# ansible-base

[![CI](https://github.com/goabonga/ansible-base/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/goabonga/ansible-base/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/goabonga/ansible-base/blob/main/LICENSE)
[![cookiecutter](https://img.shields.io/badge/cookiecutter-template-D4AA00.svg)](https://cookiecutter.readthedocs.io/)

A [cookiecutter](https://cookiecutter.readthedocs.io/) template that generates
a complete Ansible project for **disposable KVM/QEMU labs on a local
workstation**: an isolated libvirt NAT network, a dedicated SSH keypair, and
guests booted from a cloud image through cloud-init.

What you get is not a bare skeleton — the generated repository ships with the
full toolchain already wired: uv, yamllint, ansible-lint at its `production`
profile, ruff, pre-commit, SPDX header enforcement, Conventional-Commit
releasing through [multicz](https://github.com/goabonga/multicz), signed
Dependabot, and a GitHub Actions pipeline that lints, audits and releases.

## Usage

```bash
uvx cookiecutter gh:goabonga/ansible-base
```

Or from a local clone:

```bash
uvx cookiecutter /path/to/ansible-base
```

## Variables

| Variable | Default | What it drives |
| --- | --- | --- |
| `project_name` | `Ansible Lab` | Human-readable name |
| `project_slug` | derived from `project_name` | Directory, Python project name, multicz component |
| `project_description` | … | `pyproject.toml`, README lead |
| `author_name` / `author_email` | `Chris` / `goabonga@pm.me` | Authorship, SPDX headers, security contact |
| `github_user` | `goabonga` | Repository URLs, badges, Galaxy role namespace |
| `year` | `2026` | Copyright year in every SPDX header |
| `lab_network_name` | `{{ project_slug }}` | libvirt network name |
| `lab_network_bridge` | `virbr-lab` | Bridge interface (**max 15 characters**) |
| `lab_network_domain` | `{{ project_slug }}.lab` | DNS domain handed to the guests |
| `lab_network_subnet` | `192.168.170` | First three octets of the lab `/24` |
| `lab_base_image` | `ubuntu-24.04-noble` | Cloud image and default guest user |

`lab_base_image` also picks the unprivileged account cloud-init creates —
`ubuntu` for the Ubuntu images, `debian` for the Debian one.

Give each lab its own `lab_network_subnet` if you expect to run several side
by side; two projects sharing a range will fight over the libvirt network.

## Validation

`hooks/pre_gen_project.py` rejects bad answers **before** any file is written:
a `project_slug` that is not a usable Python project name, a
`lab_network_bridge` longer than the kernel's `IFNAMSIZ` limit of 15
characters, or a malformed subnet. You get an error message instead of a
project that only fails later, deep inside a libvirt call.

## How the Jinja conflict is handled

Ansible and cookiecutter both use `{{ ... }}`, so rendering the Ansible
sources through cookiecutter would destroy every `{{ lab_state_dir }}` and
`{{ inventory_hostname }}` in the tree. This template deals with it in three
layers:

1. **`_copy_without_render`** — the roles, the playbooks and the `.j2`
   templates are copied verbatim. They contain no cookiecutter variables, so
   they lose nothing.
2. **`{% raw %}` guards** — `inventory/group_vars/all.yml` and
   `.github/workflows/ci.yml` genuinely need both syntaxes. Their Ansible and
   GitHub expressions sit inside `raw` blocks; only the handful of
   cookiecutter substitutions stay live.
3. **`hooks/post_gen_project.py`** — because the verbatim-copied files never
   pass through Jinja, their SPDX copyright line would still name the template
   author. The hook rewrites it across the whole generated tree, which is what
   keeps `scripts/add_license_header.py --check` green in the generated CI.

The upshot: the Ansible sources stay readable, with no `{% raw %}` noise
scattered through them.

## Developing the template

```bash
uv run pytest                    # generates a project and lints it
uvx cookiecutter --no-input .    # generate with the defaults, by hand
```

The CI pipeline generates a project from the defaults and then runs that
project's own gates against it — yamllint, ansible-lint, the playbook
syntax-check and the SPDX header check. A template that produces a repository
failing its own lint suite is a broken template, so the test suite is the
contract.

## License

Distributed under the [MIT License](LICENSE).
