# ansible-base

[![CI](https://github.com/goabonga/ansible-base/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/goabonga/ansible-base/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/goabonga/ansible-base.svg)](https://github.com/goabonga/ansible-base/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/goabonga/ansible-base/blob/main/LICENSE)
[![Ansible](https://img.shields.io/badge/ansible--core-%E2%89%A5%202.18-blue.svg)](https://docs.ansible.com/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

**Template repository.** The reusable skeleton behind every lab built on
**disposable KVM/QEMU guests on your own workstation**: an isolated libvirt
network, a dedicated SSH key, and guests booted from an Ubuntu cloud image
with cloud-init. Everything is installed natively — `systemctl status`
behaves the way you expect on a normal server.

```text
   workstation (libvirt / qemu:///system)
   ├── network ansible-lab  192.168.170.0/24  NAT
   └── (guests declared in inventory/local.yml)
```

The host preparation and the guest factory ship here. The guests themselves,
and what runs on them, come from the project you derive from this one.

## Requirements

- A Linux workstation with hardware virtualisation (`/dev/kvm`) and `sudo`
- [uv](https://docs.astral.sh/uv/) — it installs Ansible and the linters
- Internet access on the first run (the cloud image is ~600 MiB)

The `kvm-host` playbook installs libvirt, QEMU and the rest on the
workstation; nothing else has to be prepared by hand.

## Using this template

Start a new project from it — *Use this template* on GitHub, or clone and
reset the history:

```bash
git clone https://github.com/goabonga/ansible-base.git ansible-myproject
cd ansible-myproject
rm -rf .git && git init
```

Then rename, in this order:

| What | Where |
| --- | --- |
| Project name and description | `pyproject.toml` (`name`, `description`, `keywords`, `[project.urls]`) |
| multicz component | `multicz.toml` — `[components.ansible-base]` |
| Release version lookup | `.github/workflows/ci.yml` — `multicz get ansible-base` (2 occurrences) |
| Lab identity | `inventory/group_vars/all.yml` — `lab_state_dir`, `lab_network_name`, `lab_network_bridge`, `lab_network_domain` |
| Cloud-init marker | `roles/vm/templates/user-data.j2` — `/etc/ansible-base-lab` |
| SSH key comment | `roles/kvm_host/defaults/main.yml` — `kvm_host_ssh_key_comment` |
| Docs and badges | `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/` |
| Galaxy collections | `requirements.yml` — add what the new roles need |

Give the lab its own network range too if you expect to run several labs side
by side: `192.168.170.0/24` is the default here, and two projects sharing it
will fight over the libvirt network.

Finally, `uv lock` to refresh the lockfile with the new project name, and
`git commit` as `feat: ...` so multicz cuts the first release.

## Getting started

```bash
uv sync                                                  # Ansible + linters
uv run ansible-galaxy collection install -r requirements.yml

uv run ansible-playbook playbooks/site.yml --ask-become-pass
```

If you prefer a plain shell, `source .venv/bin/activate` once and drop the
`uv run` prefix from every command below.

The sudo password is only used on the workstation (packages, libvirt, guest
disks); the guests themselves are driven with a passwordless key that the
first play generates in `~/.local/share/ansible-base/`.

## Declaring a guest

Add it to the `lab` group and run `provision.yml`. The address is applied by
cloud-init, so it only has to be inside the lab network and outside the DHCP
range (`.100`–`.200`):

```yaml
# inventory/local.yml
lab:
  children:
    web:
      hosts:
        web-1:
          vm_ip: 192.168.170.10
          vm_mac: "52:54:00:17:0a:0a"
          vm_memory_mb: 2048
          vm_vcpus: 2
          vm_disk_size: 20G
```

Each guest boots a thin qcow2 overlay on the shared base image, so a new one
costs seconds and a few MiB.

## Playbooks

| Playbook | What it does |
| --- | --- |
| `playbooks/site.yml` | The whole lab, in order |
| `playbooks/kvm-host.yml` | Workstation: packages, libvirt, lab keypair, NAT network |
| `playbooks/provision.yml` | Creates the guests and waits for cloud-init |
| `playbooks/destroy.yml` | Removes the guests, their disks and their seeds |

A derived project adds its own playbooks after `provision.yml` and wires them
into `site.yml`.

Rebuild from scratch (the base cloud image is kept, so it takes seconds):

```bash
uv run ansible-playbook playbooks/destroy.yml --ask-become-pass
uv run ansible-playbook playbooks/site.yml --ask-become-pass
```

Add `-e lab_destroy_network=true` to remove the libvirt network as well.

## Customising

Everything lives in the inventory; the roles only hold defaults.

| File | Typical change |
| --- | --- |
| `inventory/local.yml` | Guests: sizing, addresses, groups |
| `inventory/group_vars/all.yml` | Network plan, base image, lab paths |

**Different image** — point `lab_image_url` and `lab_image_checksum_url` at
another cloud image; anything cloud-init based and Debian-flavoured works.

## Layout

```text
ansible-base/
├── ansible.cfg
├── inventory/
│   ├── local.yml              # the guests and the workstation
│   └── group_vars/
├── playbooks/
├── roles/
│   ├── kvm_host/              # libvirt, lab keypair, NAT network
│   └── vm/                    # cloud image overlay + NoCloud seed + domain
├── requirements.yml           # Galaxy collections
└── multicz.toml               # versioning and changelog
```

## Development

```bash
uv run yamllint --strict .
uv run ansible-lint
uv run ansible-playbook --syntax-check playbooks/*.yml
uv run pre-commit install      # pre-commit + commit-msg hooks
```

`ansible-lint` runs at its `production` profile, and the same gates run in CI
on Python 3.11 and 3.12.

## Versioning and release

Versions are bumped from
[Conventional Commits](https://www.conventionalcommits.org/) by
[multicz](https://github.com/goabonga/multicz). On every push to `main`, CI
computes the bump, writes the changelog, tags and creates the GitHub release.
Only changes under `roles/`, `playbooks/`, `inventory/`, `ansible.cfg`,
`requirements.yml` and `pyproject.toml` count as releasable. Maintainers do not
bump versions or edit the changelog by hand.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow, the commit-message
convention, and the lint expectations. By participating you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md).

Security issues: please follow the disclosure process in
[SECURITY.md](SECURITY.md).

## License

Distributed under the [MIT License](LICENSE).
