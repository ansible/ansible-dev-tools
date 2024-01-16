# Using the CI workflow

The following GitHub Actions are to be placed added under `.github/workflows` directory as `{filename}.yaml`
This GitHub Actions workflow automates a range of tasks integral to Ansible content development, encompassing changelog generation, linting, integration, sanity checks, and unit tests. The all_green job serves the purpose of verifying the successful completion of all preceding tasks.

Filename: `test.yaml`

```
---
name: "CI"

concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true

on:
  pull_request:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *'

jobs:
  changelog:
    uses: ansible/ansible-content-actions/.github/workflows/changelog.yaml@main
    if: github.event_name == 'pull_request'
  ansible-lint:
    uses: ansible/ansible-content-actions/.github/workflows/ansible_lint.yaml@main
  sanity:
    uses: ansible/ansible-content-actions/.github/workflows/sanity.yaml@main
  unit-galaxy:
    uses: ansible/ansible-content-actions/.github/workflows/unit.yaml@main
  integration:
    uses: ansible/ansible-content-actions/.github/workflows/integration.yaml@main
  all_green:
    if: ${{ always() }}
    needs:
      - changelog
      - sanity
      - integration
      - unit-galaxy
      - ansible-lint
    runs-on: ubuntu-latest
    steps:
      - run: >-
          python -c "assert 'failure' not in
          set([
          '${{ needs.changelog.result }}',
          '${{ needs.integration.result }}',
          '${{ needs.sanity.result }}',
          '${{ needs.unit-galaxy.result }}',
          '${{ needs.ansible-lint.result }}'
          ])"
```

The workflow run results in -

![Alt text](./images/ci.png?raw=true "CI Run")

The workflow uses tox-ansible, pytest-ansible to generate the matrix, which is used to run unit, sanity and integration tests.

Refer to the [tox-ansible documentation] to see more options.

[pytest-ansible]: https://ansible.readthedocs.io/projects/pytest-ansible/
[tox-ansible documentation]: https://ansible.readthedocs.io/projects/tox-ansible/
