# Contributing to ansible-base

Thanks for taking the time to contribute. This document is the short version
of how to propose a change and what the project expects in return.

## Code of Conduct

Participation in this project is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md). By contributing you agree to abide by
its terms.

## Development setup

```bash
git clone https://github.com/goabonga/ansible-base.git
cd ansible-base
uv sync
uv run pre-commit install   # installs the pre-commit + commit-msg hooks
uv run ansible-galaxy collection install -r requirements.yml
```

## Quality gates

Before pushing, make sure your change passes the same gates the `ci` workflow
runs:

```bash
uv run yamllint .
uv run ansible-lint
uv run ansible-playbook --syntax-check playbooks/*.yml
uv run ruff check scripts && uv run ruff format --check scripts
uv tool run multicz validate --strict
uv run python scripts/add_license_header.py --path roles --types yml --check
```

There is no automated test that boots the lab, so a change to the roles has
to be exercised by hand: `playbooks/destroy.yml` then `playbooks/site.yml`
against a real libvirt host, and say so in the pull request.

## Commit messages

Commit messages MUST follow
[Conventional Commits](https://www.conventionalcommits.org/). They drive the
version bump and CHANGELOG computed by
[multicz](https://github.com/goabonga/multicz).

| Type | Effect on version | Use it for |
| --- | --- | --- |
| `feat` | minor | new capability |
| `fix` | patch | bug fix |
| `perf` | patch | performance improvement |
| `refactor`, `docs`, `test`, `chore`, `ci`, `build`, `style` | none | maintenance |
| `feat!` / `BREAKING CHANGE:` | major | incompatible change |

Only commits that touch the tracked paths trigger a release: `roles/**`,
`playbooks/**`, `inventory/**`, `ansible.cfg`, `requirements.yml` and
`pyproject.toml` (see `multicz.toml`). Documentation, governance and CI
changes never ship a version. Do not append `Co-Authored-By` trailers.

## Releasing

Releases are automated: on every push to `main`, the `ci` workflow runs
`multicz bump` (signed commit + tag) and creates the GitHub release.
Maintainers do not bump versions or edit the changelog by hand.

## Reporting bugs and asking for features

Please open a GitHub issue. For security-sensitive reports, follow
[SECURITY.md](SECURITY.md) instead of the public tracker.
