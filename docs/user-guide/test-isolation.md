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

- Prefer being run from within a **writable** python virtual environment,
  warning the user if this not the case.
- Dynamically modify Ansible environment to prefer installation of dependencies
  such as collections, roles and python packages inside the current virtual
  environment.

## Isolated mode (default)

- First folder that is not read-only from the list below will be used as cache directory and also :
  - `$VIRTUAL_ENV/.ansible` for anything but collections, those will be inside `lib/python3.*/site-packages/ansible_collections` because this makes them available to ansible-core without any additional configuration.
  - `$PROJECT_ROOT/.ansible`
  - `$TMPDIR/.ansible-<sha256>` for temporary installations

- `ANSIBLE_HOME` will be defined to point to it, preventing accidental use of user's home directory. Its existing value will be ignored. If you want to avoid this, see non-isolated mode below.

### Virtual environment detection

Our tools will look for presence of `VIRTUAL_ENV` variable and use it.
Otherwise they will also try to look a `.venv` directory inside
the project directory will try to use it if found.

When running ansible-dev-tools inside a **writable** virtual environment,
the following things will happen:

- Few Ansible environment variables will be automatically defined in order to
  make `ansible-galaxy` install commands to install content (collections and
  roles) directly inside the virtual environment. Ansible-core itself is
  already able to find content from inside the virtual environment and this
  takes priority over the other paths.
- Dependencies will automatically be installed inside the virtual environment

## Non-isolated mode

No changing of ansible include paths will be performed, and a warning will be
displayed telling user that its user environment is not isolated and that
result of tool execution may produce unpredictable results on other systems.

The cache directory will point to `$ANSIBLE_HOME/tmp/compat-ZZZ`, where ZZZ is
a sha256 hash of the project directory.

## Offline mode

Tools like ansible-lint provide an option `--offline` that will disable their
ability to install any dependencies. This does not mean that they will run
successfully without the dependencies, it just means that they user takes
the responsibility to pre-install these before running the tools.

---

[moleclue]: https://docs.ansible.com/projects/molecule/
[ansible-lint]: https://docs.ansible.com/projects/lint/
[ansible-dev-environment]: https://docs.ansible.com/projects/dev-environment/
