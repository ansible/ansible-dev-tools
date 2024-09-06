<!-- cspell:disable-next-line -->

# Ansible Development Tools (ADT)

The `ansible-dev-tools` python package provides an easy way to install and discover the best tools available to create and test ansible content.

The curated list of tools installed as part of the Ansible automation developer tools package includes:

[ansible-core](https://github.com/ansible/ansible): Ansible is a radically simple IT automation platform that makes your applications and systems easier to deploy and maintain. Automate everything from code deployment to network configuration to cloud management, in a language that approaches plain English, using SSH, with no agents to install on remote systems.

[ansible-builder](https://github.com/ansible/ansible-builder): Ansible Builder is a tool that automates the process of building execution environments using the schemas and tooling defined in various Ansible Collections and by the user.

[ansible-creator](https://github.com/ansible/ansible-creator): The fastest way to generate all your ansible content!

[ansible-lint](https://github.com/ansible/ansible-lint): Checks playbooks for practices and behavior that could potentially be improved.

[ansible-navigator](https://github.com/ansible/ansible-navigator) A text-based user interface (TUI) for Ansible.

[ansible-sign](https://github.com/ansible/ansible-sign): Utility for signing and verifying Ansible project directory contents.

[molecule](https://github.com/ansible/molecule): Molecule aids in the development and testing of Ansible content: collections, playbooks and roles

[pytest-ansible](https://github.com/ansible/pytest-ansible): A pytest plugin that enables the use of ansible in tests, enables the use of pytest as a collection unit test runner, and exposes molecule scenarios using a pytest fixture.

[tox-ansible](https://github.com/ansible/tox-ansible): The tox-ansible plugin dynamically creates a full matrix of python interpreter and ansible-core version environments for running integration, sanity, and unit for an ansible collection both locally and in a Github action. tox virtual environments are leveraged for collection building, collection installation, dependency installation, and testing.

[ansible-dev-environment](https://github.com/ansible/ansible-dev-environment): A pip-like install for Ansible collections.

## Communication

Refer to our [Communication guide](https://ansible.readthedocs.io/projects/dev-tools/contributor-guide/#talk-to-us) for details.

## Installation

`python3 -m pip install ansible-dev-tools`

A VsCode compatible devcontainer is also available which is a great way to develop ansible content. The image name is [community-ansible-dev-tools](https://ansible.readthedocs.io/projects/dev-tools/container/).

## Usage

In addition to installing each of the above tools, `ansible-dev-tools` provides an easy way to show the versions of the content creation tools that make up the current development environment.

```
$ adt --version
ansible-builder                          <version>
ansible-core                             <version>
ansible-creator                          <version>
ansible-dev-environment                  <version>
ansible-dev-tools                        <version>
ansible-lint                             <version>
ansible-navigator                        <version>
ansible-sign                             <version>
molecule                                 <version>
pytest-ansible                           <version>
tox-ansible                              <version>
```

## Developer Notes

The `ansible-dev-tools` package also offers an Ansible Devtools server which can be launched with `adt server`. Currently, this server only supports REST APIs for `ansible-creator`.

Refer to the [server](https://github.com/ansible/ansible-dev-tools/blob/main/src/ansible_dev_tools/subcommands/server.py) code for available endpoints.

To run this server from the community dev-tools container, use the following command:

```
$ podman run -d -p 8000:8000 --name=ansible-devtools-server ghcr.io/ansible/community-ansible-dev-tools:latest adt server
778d0423863c5c161b4bdcb6177d169f0897c597ff084c7a0d3401814d78174f
$ podman logs -f ansible-devtools-server
[2024-04-25 17:28:02 +0000] [10] [INFO] Starting gunicorn 22.0.0
[2024-04-25 17:28:02 +0000] [10] [INFO] Listening at: http://0.0.0.0:8000 (10)
[2024-04-25 17:28:02 +0000] [10] [INFO] Using worker: sync
[2024-04-25 17:28:02 +0000] [11] [INFO] Booting worker with pid: 11
```

**Note:** This is primarily for backend integrations and is not intended to be an user-facing functionality.

## Documentation

For more information, please visit our [documentation](https://ansible.readthedocs.io/projects/dev-tools/) page.
