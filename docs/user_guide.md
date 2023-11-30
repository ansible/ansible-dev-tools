# User Guide

## Ensure content best practices

### (A) Add a tox entry for lint in CI

Integrating lint into your Continuous Integration (CI) pipeline ensures that your codebase adheres to coding standards and best practices.

To add Tox Entry for Linting:

1. Create a `tox.ini` file in the root of your project. This will contain the configuration for running various environments.
2. Update your CI configuration file (e.g., `.github/workflows/main.yml` for GitHub Actions) to include the tox command with the linting environment.
3. Commit the changes to your repository and push them to trigger the CI pipeline.

With this you have successfully added a tox entry for linting in your CI setup i.e. `tox -e lint`. This ensures that lint checks are automatically performed whenever changes are pushed to the repository, helping maintain a clean and consistent codebase.

### (B) Run sanity tests using tox-ansible

Tox-ansible uses `ansible-test sanity` to run the sanity tests. After installing `tox-ansible`, create an empty `tox-ansible.ini` file from the root of your collection and list the available environments:

```bash
touch tox-ansible.ini
tox list --ansible --conf tox-ansible.ini
```

A list of dynamically generated Ansible environments will be displayed:

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

To run tests with a single environment, simply run the following command:

```bash
tox -e sanity-py3.11-2.14 --ansible --conf tox-ansible.ini
```

To run tests with multiple environments, simply add the environment names to the command:

```bash
tox -e sanity-py3.11-2.14,sanity-py3.11-devel --ansible --conf tox-ansible.ini
```

Please refer to this official [tox-ansible documentation] to see more options.

[tox-ansible documentation]: https://ansible.readthedocs.io/projects/tox-ansible/
