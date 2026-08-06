# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Chris <goabonga@pm.me>

"""The template's contract: a generated project must pass its own gates.

A cookiecutter that renders cleanly but produces a repository failing its own
lint suite is a broken cookiecutter, so these tests generate a project and
then run the very commands its CI runs.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE = Path(__file__).resolve().parent.parent

# Deliberately different from every default, so a value that failed to be
# substituted shows up as the template's own default leaking through.
CONTEXT = {
    "project_name": "Edge Lab",
    "project_description": "Provisions the edge testbed.",
    "author_name": "Ada Lovelace",
    "author_email": "ada@example.org",
    "github_user": "adalovelace",
    "year": "2031",
    "lab_network_bridge": "virbr-edge",
    "lab_network_subnet": "10.42.7",
}


def run(*argv: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True)


@pytest.fixture(scope="session")
def project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output = tmp_path_factory.mktemp("generated")
    cookiecutter(
        str(TEMPLATE), no_input=True, extra_context=CONTEXT, output_dir=str(output)
    )
    generated = output / "edge-lab"
    assert generated.is_dir(), f"expected {generated}, got {list(output.iterdir())}"
    return generated


def test_slug_is_derived_from_the_name(project: Path) -> None:
    assert project.name == "edge-lab"


def test_no_unrendered_cookiecutter_variable_survives(project: Path) -> None:
    """A stray `{{ cookiecutter.x }}` means a file was rendered but a variable
    was misspelled, or a file landed in `_copy_without_render` by mistake."""
    leaked = [
        path.relative_to(project)
        for path in project.rglob("*")
        if path.is_file() and "cookiecutter" in path.read_text(errors="ignore")
    ]
    assert not leaked, f"cookiecutter variables leaked into: {leaked}"


def test_ansible_expressions_survived_rendering(project: Path) -> None:
    """The mirror image: Ansible's own `{{ ... }}` must come out untouched."""
    user_data = (project / "roles/vm/templates/user-data.j2").read_text()
    assert "{{ inventory_hostname }}" in user_data
    assert "{{ vm_ssh_public_key | trim }}" in user_data

    all_yml = (project / "inventory/group_vars/all.yml").read_text()
    assert "{{ lookup('ansible.builtin.env', 'HOME') }}" in all_yml
    assert "{{ lab_state_dir }}/id_ed25519" in all_yml
    # ...while the cookiecutter substitutions in that same file did happen.
    assert "/.local/share/edge-lab" in all_yml
    assert "lab_network_gateway: 10.42.7.1" in all_yml
    assert "lab_network_bridge: virbr-edge" in all_yml


def test_github_expressions_survived_rendering(project: Path) -> None:
    ci = (project / ".github/workflows/ci.yml").read_text()
    assert "${{ matrix.python-version }}" in ci
    assert "${{ github.job }}" in ci
    # The one thing that *had* to be substituted inside that raw block.
    assert "multicz get edge-lab" in ci
    assert "ansible-base" not in ci


def test_project_metadata_is_substituted(project: Path) -> None:
    pyproject = (project / "pyproject.toml").read_text()
    assert 'name = "edge-lab"' in pyproject
    assert 'description = "Provisions the edge testbed."' in pyproject
    assert (
        'authors = [{ name = "Ada Lovelace", email = "ada@example.org" }]' in pyproject
    )
    assert "https://github.com/adalovelace/edge-lab" in pyproject
    assert "[components.edge-lab]" in (project / "multicz.toml").read_text()


def test_copyright_header_rewritten_everywhere(project: Path) -> None:
    """Including the files copied verbatim, which never pass through Jinja."""
    expected = "# Copyright (c) 2031 Ada Lovelace <ada@example.org>"
    stale = re.compile(r"^# Copyright \(c\) (?!2031 Ada Lovelace)", re.MULTILINE)

    verbatim = project / "roles/vm/tasks/main.yml"
    assert expected in verbatim.read_text(), (
        "a _copy_without_render file kept the old header"
    )

    offenders = [
        path.relative_to(project)
        for path in project.rglob("*")
        if path.is_file() and stale.search(path.read_text(errors="ignore"))
    ]
    assert not offenders, f"stale copyright header in: {offenders}"


def test_header_matches_what_the_checker_enforces(project: Path) -> None:
    """`add_license_header.py` carries its own copy of the expected header;
    if the hook and the script disagree, the generated CI fails on day one."""
    script = (project / "scripts/add_license_header.py").read_text()
    assert '"# Copyright (c) 2031 Ada Lovelace <ada@example.org>",' in script


@pytest.mark.parametrize(
    "image,expected_user,expected_image",
    [
        ("ubuntu-24.04-noble", "ubuntu", "noble-server-cloudimg-amd64.img"),
        ("debian-12-bookworm", "debian", "debian-12-generic-amd64.qcow2"),
    ],
)
def test_base_image_choice_picks_the_matching_user(
    tmp_path: Path, image: str, expected_user: str, expected_image: str
) -> None:
    cookiecutter(
        str(TEMPLATE),
        no_input=True,
        extra_context={**CONTEXT, "lab_base_image": image},
        output_dir=str(tmp_path),
    )
    all_yml = (tmp_path / "edge-lab/inventory/group_vars/all.yml").read_text()
    assert f"lab_vm_user: {expected_user}" in all_yml
    assert f"lab_image_name: {expected_image}" in all_yml


@pytest.mark.parametrize(
    "bad_context,reason",
    [
        ({"lab_network_bridge": "virbr-far-too-long-for-the-kernel"}, "IFNAMSIZ"),
        ({"lab_network_subnet": "192.168"}, "malformed subnet"),
        ({"project_name": "Not A Slug!"}, "unusable slug"),
    ],
)
def test_pre_gen_hook_rejects_bad_answers(
    tmp_path: Path, bad_context: dict, reason: str
) -> None:
    from cookiecutter.exceptions import FailedHookException

    with pytest.raises(FailedHookException):
        cookiecutter(
            str(TEMPLATE),
            no_input=True,
            extra_context={**CONTEXT, **bad_context},
            output_dir=str(tmp_path),
        )


def test_generated_yaml_is_valid_json_free(project: Path) -> None:
    """cookiecutter.json itself must stay parseable — a trailing comma here
    breaks every generation with an opaque error."""
    json.loads((TEMPLATE / "cookiecutter.json").read_text())


@pytest.mark.skipif(shutil.which("yamllint") is None, reason="yamllint not installed")
def test_generated_project_passes_yamllint(project: Path) -> None:
    result = run("yamllint", "--strict", ".", cwd=project)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(shutil.which("ansible-lint") is None, reason="ansible-lint missing")
def test_generated_project_passes_ansible_lint(project: Path) -> None:
    result = run("ansible-lint", cwd=project)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(shutil.which("ansible-playbook") is None, reason="ansible missing")
def test_generated_playbooks_parse(project: Path) -> None:
    playbooks = sorted(str(p) for p in (project / "playbooks").glob("*.yml"))
    result = run("ansible-playbook", "--syntax-check", *playbooks, cwd=project)
    assert result.returncode == 0, result.stdout + result.stderr


def test_generated_project_passes_its_own_header_check(project: Path) -> None:
    result = run(
        sys.executable,
        "scripts/add_license_header.py",
        "--path",
        "roles",
        "--types",
        "yml",
        "--check",
        cwd=project,
    )
    assert result.returncode == 0, result.stdout + result.stderr
