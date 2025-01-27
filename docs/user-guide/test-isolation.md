# Test Isolation

!!! note

    The test isolation behaviors described below are expected to be fully implemented
    by the end of **February 2025** and will affect [ansible-lint][ansible-lint], [molecule][molecule] and [ansible-dev-environment (ade)][ansible-dev-environment] in particular.

One very common problem in software development is reproducibility of test
results across the various environments:

- local development, aka "works on my machine"
- CI/CD testing pipelines
- staging and production environments

A very common source of producing divergent results across these are the
dependencies, which can be:

- used dependencies that are not declared but happen to be installed
  on a developer's machine
- different versions of the same dependency
- conflicts between dependencies

Historically, most of ansible-dev-tools tried to address these by installing
dependencies in a controlled way and trying to avoid installing them in the
default user home directory, as this might affect other projects in
an unpredictable way.

Starting with early 2025, all ansible-dev-tools will aim to implement the
following predictable behaviors:

- Prefer being run from within a python virtual environment, warning the user
  if this not the case.
- Dynamically modify Ansible environment to prefer installation of dependencies
  such as collections, roles and python packages inside the current virtual
  environment.

## Isolated mode (virtual environment) \[default\]

This is the recommended way to run ansible-dev-tools. If a virtual environment
is not detected, a warning will be displayed, prompting the user to use one
for better isolation.

It should be noted that our tools will look for a `.venv` directory inside
the current directory if a virtual environment is not already active and will
try to use it if found.

When running ansible-dev-tools inside a virtual environment, the following
things will happen:

- Few Ansible environment variables will be automatically defined in order to
  make `ansible-galaxy` install commands to install content (collections and
  roles) directly inside the virtual environment. Ansible-core itself is already able to find content from inside the virtual environment and this takes priority over the other paths.
- Dependencies will automatically be installed inside the virtual environment

## Non-isolated mode (outside virtual environments)

When running ansible-dev-tools outside a virtual environment, our tools will
display a warning message explaining the user that the isolation mode is
disabled.

- No alteration of ansible environment variables will be made. This is different
  from the previous behaviors of ansible-lint or molecule, which tried to define
  these to point to a temporary directory.

---

[moleclue]: https://ansible.readthedocs.io/projects/molecule/
[ansible-lint]: https://ansible.readthedocs.io/projects/lint/
[ansible-dev-environment]: https://ansible.readthedocs.io/projects/dev-environment/
