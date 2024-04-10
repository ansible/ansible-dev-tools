---
hide:
  - navigation
  - toc
---

## Requirements

- Python 3.10: ansible-dev-tools requires Python 3.10 or later. Make sure you have Python 3.10 installed on your system before proceeding.

## Installation

`pip install ansible-dev-tools`

Once installation is completed, see the [User Guide](user-guide/index.md) for more details about ansible-dev-tools usage.

### Latest Releases

- GitHub
  To view the latest releases, see the [ansible-dev-tools GitHub releases page](https://github.com/ansible/ansible-dev-tools/releases). Each release includes detailed release notes outlining new features, improvements, and bug fixes.

- PyPI
  The [PyPI page for ansible-dev-tools](https://pypi.org/project/ansible-dev-tools/) provides information on the latest stable release and allows you to download specific versions of the package.

## Upgrade

To upgrade ansible-dev-tools to the latest version, use the following pip command:

`pip install --upgrade ansible-dev-tools`

## Downgrade

If needed, you can downgrade ansible-dev-tools to a specific version using the following pip command:

`pip install ansible-dev-tools==desired-version`

## Uninstallation

If you need to uninstall ansible-dev-tools, use the following pip command:

`pip uninstall ansible-dev-tools`

## Usage

In addition to installing each of the above tools, `ansible-dev-tools` provides an easy way to show the versions of the content creation tools that make up the current development environment.

```console exec="1" source="console" returncode="0"
$ adt --version
```
