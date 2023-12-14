# Ensure content best practices

## Add a tox entry for lint in CI

Integrating lint into your Continuous Integration (CI) pipeline ensures that your codebase adheres to coding standards and best practices.

To add Tox Entry for Linting:

1. Create a `tox.ini` file in the root directory of your project. This file will contain the configuration for running various environments.

```ini
# tox.ini
[tox]
env_list = lint

[testenv:lint]
deps =
    pre-commit
    # Add other linters as needed
commands =
    pre-commit run --show-diff-on-failure --all-files
```

2. Update your CI configuration file (for example `.github/workflows/main.yml` for GitHub Actions) to include the tox command with the linting environment.
3. Commit the changes to your repository and push them, to trigger the CI pipeline.

You have successfully added a tox entry for linting (`tox -e lint`) in your CI setup. This ensures that lint checks are automatically performed whenever changes are pushed to the repository, helping maintain a clean and consistent codebase.

## Run sanity tests using tox-ansible

Tox-ansible uses `ansible-test sanity` to run sanity tests. After installing `tox-ansible`, create an empty `tox-ansible.ini` file in the root directory of your collection and list the available environments:

```bash
touch tox-ansible.ini
tox list --ansible --conf tox-ansible.ini
```

A list of dynamically generated Ansible environments is displayed:

```

default environments:
...
integration-py3.11-2.14      -> Integration tests for ansible.scm using ansible-core 2.14 and python 3.11
...
sanity-py3.11-2.14           -> Sanity tests for ansible.scm using ansible-core 2.14 and python 3.11
sanity-py3.11-devel          -> Sanity tests for ansible.scm using ansible-core devel and python 3.11
sanity-py3.11-milestone      -> Sanity tests for ansible.scm using ansible-core milestone and python 3.11
...
unit-py3.11-2.14             -> Unit tests for ansible.scm using ansible-core 2.14 and python 3.11
```

To run tests with a single environment, run the following command:

```bash
tox -e sanity-py3.11-2.14 --ansible --conf tox-ansible.ini
```

To run tests with multiple environments, add the environment names to the command:

```bash
tox -e sanity-py3.11-2.14,sanity-py3.11-devel --ansible --conf tox-ansible.ini
```

Refer to the [tox-ansible documentation] to see more options.

[tox-ansible documentation]: https://ansible.readthedocs.io/projects/tox-ansible/
