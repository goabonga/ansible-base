#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Chris <goabonga@pm.me>

# Rewrites the SPDX copyright line across the generated project.
#
# Most of the Ansible content is listed in `_copy_without_render` because it
# is full of double-brace expressions that belong to Ansible, not to
# cookiecutter. Those files are copied verbatim, so their copyright line would
# otherwise still name the template author. This hook fixes them after the
# fact, which keeps the Ansible sources free of Jinja raw-block noise while
# still satisfying `scripts/add_license_header.py --check` in CI.
#
# NB: this file is itself rendered by cookiecutter before it runs, so it must
# not contain stray Jinja syntax in comments or strings.

import os
import re

COPYRIGHT = (
    "# Copyright (c) {{ cookiecutter.year }} "
    "{{ cookiecutter.author_name }} <{{ cookiecutter.author_email }}>"
)
COPYRIGHT_RE = re.compile(r"^# Copyright \(c\) .*$", re.MULTILINE)

# Only the first few lines can hold the header; rewriting further down would
# corrupt a file that merely mentions a copyright in prose.
HEADER_LINES = 5

PRUNE_DIRS = {".git", ".venv", "collections", "__pycache__", ".ruff_cache"}

rewritten = 0

for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
    for filename in filenames:
        path = os.path.join(dirpath, filename)
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.readlines()
        except (UnicodeDecodeError, OSError):
            continue

        head = lines[:HEADER_LINES]
        patched = [
            COPYRIGHT_RE.sub(COPYRIGHT, line.rstrip("\n")) + "\n" for line in head
        ]
        if patched == head:
            continue

        with open(path, "w", encoding="utf-8") as handle:
            handle.writelines(patched + lines[HEADER_LINES:])
        rewritten += 1

print(f"Rewrote the copyright header in {rewritten} file(s).")
print(
    "\nNext steps:\n"
    "  cd {{ cookiecutter.project_slug }}\n"
    "  git init && git add -A && git commit -m 'feat: initial lab'\n"
    "  uv sync && uv run ansible-galaxy collection install -r requirements.yml\n"
    "  uv run ansible-playbook playbooks/site.yml --ask-become-pass\n"
)
