## Description

<!-- Describe what this PR does and why. -->

## Type

<!-- Check the one that applies: -->

- [ ] `feat` - New feature
- [ ] `fix` - Bug fix
- [ ] `docs` - Documentation
- [ ] `refactor` - Code refactoring
- [ ] `test` - Adding or updating tests
- [ ] `chore` - Maintenance
- [ ] `ci` - CI / release pipeline

## Changes

<!-- List the main changes introduced by this PR: -->

-

## Related Issues

<!-- Link related issues: Closes #123, Fixes #456 -->

## Checklist

- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] Branch is up to date with `main`
- [ ] `uv sync` succeeds
- [ ] `uv run yamllint .` is clean
- [ ] `uv run ansible-lint` is clean
- [ ] `uv run ansible-playbook --syntax-check playbooks/*.yml` passes
- [ ] `uv run ruff check scripts` and `uv run ruff format --check scripts` are clean
- [ ] `uv tool run multicz validate --strict` passes
- [ ] SPDX license headers are present (`uv run python scripts/add_license_header.py --path roles --types yml --check`)
- [ ] The lab was rebuilt against a real libvirt host (`playbooks/destroy.yml` then `playbooks/site.yml`), or the change cannot affect it
- [ ] No `Co-Authored-By` trailer in commit messages
