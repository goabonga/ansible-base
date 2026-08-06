#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Chris <goabonga@pm.me>

# Validates the answers before a single file is written, so a bad value fails
# loudly instead of producing a project that only breaks at `ansible-playbook`
# time.

import re
import sys

PROJECT_SLUG = "{{ cookiecutter.project_slug }}"
NETWORK_BRIDGE = "{{ cookiecutter.lab_network_bridge }}"
NETWORK_NAME = "{{ cookiecutter.lab_network_name }}"
NETWORK_SUBNET = "{{ cookiecutter.lab_network_subnet }}"

SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$")
# Linux caps interface names at IFNAMSIZ (16 bytes including the NUL), so a
# bridge name longer than 15 characters is rejected by the kernel, not by
# libvirt — the failure surfaces as an opaque network-start error.
IFNAMSIZ = 15
SUBNET_RE = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")

errors = []

if not SLUG_RE.match(PROJECT_SLUG):
    errors.append(
        f"project_slug {PROJECT_SLUG!r} must be lowercase alphanumeric with "
        "dashes, starting with a letter (it becomes the Python project name)."
    )

if len(NETWORK_BRIDGE) > IFNAMSIZ:
    errors.append(
        f"lab_network_bridge {NETWORK_BRIDGE!r} is {len(NETWORK_BRIDGE)} "
        f"characters; the Linux kernel refuses interface names over {IFNAMSIZ}."
    )

if not NETWORK_NAME:
    errors.append("lab_network_name must not be empty.")

match = SUBNET_RE.match(NETWORK_SUBNET)
if not match:
    errors.append(
        f"lab_network_subnet {NETWORK_SUBNET!r} must be the first three octets "
        "of a /24, for example 192.168.170."
    )
elif any(int(octet) > 255 for octet in match.groups()):
    errors.append(f"lab_network_subnet {NETWORK_SUBNET!r} has an octet over 255.")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    sys.exit(1)
