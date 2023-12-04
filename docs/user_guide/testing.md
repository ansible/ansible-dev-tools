# Testing a user-facing role within a collection

## Molecule

To set up molecule, create a new directory in your collection called
extensions, and inside that directory, run molecule init scenario to create
the default scenario.

```
mkdir extensions
cd extensions
molecule init scenario
```

add collection path to molecule.yml
https://ansible.readthedocs.io/projects/molecule/configuration/

include role in converge.yml

```
---
- name: Include a role from a collection
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Testing role
      ansible.builtin.include_role:
        name: foo.bar.my_role
        tasks_from: main.yml
```

or a playbook:

```
---
- name: Include a playbook from a collection
  ansible.builtin.import_playbook: foo.bar.my_playbook
```

molecule test

## pytest-ansible

By adding a special test to tests/integration, your molecule tests can be run
alongside your unit tests with pytest-ansible

```
"""Tests for molecule scenarios."""
from __future__ import absolute_import, division, print_function

from pytest_ansible.molecule import MoleculeScenario


def test_integration(molecule_scenario: MoleculeScenario) -> None:
    """Run molecule for each scenario.

    :param molecule_scenario: The molecule scenario object
    """
    proc = molecule_scenario.test()
    assert proc.returncode == 0
```

Calling pytest will now run your molecule scenarios as a pytest job.

## tox-ansible

tox-ansible automates the running of your pytest tests on many different Python
and Ansible versions.

To start, create an empty tox-ansible.ini in your collection root:

```
touch tox-ansible.ini
```

This will be the configuration file for tox-ansible. We always start with an
empty file to avoid unintentionally overriding tox-ansible environment
configurations.

To list the generated environments that can be run, call `tox list --ansible -c tox-ansible.ini`

```
default environments:
...
integration-py3.11-2.14      -> Integration tests using ansible-core 2.16 and python 3.12
integration-py3.11-devel     -> Integration tests using ansible-core devel and python 3.12
integration-py3.11-milestone -> Integration tests using ansible-core milestone and python 3.12
...
sanity-py3.11-2.14           -> Sanity tests using ansible-core 2.16 and python 3.12
sanity-py3.11-devel          -> Sanity tests using ansible-core devel and python 3.12
sanity-py3.11-milestone      -> Sanity tests using ansible-core milestone and python 3.12
...
unit-py3.11-2.14             -> Unit tests using ansible-core 2.16 and python 3.12
unit-py3.11-devel            -> Unit tests using ansible-core devel and python 3.12
unit-py3.11-milestone        -> Unit tests using ansible-core milestone and python 3.12
```

This is limited to supported combinations, so tests may be run on Python 3.8
with `ansible-core` 2.12, but not with `ansible-core` 2.14. Versions of
ansible-core can be skipped in the tox-ansible.ini file in the `ansible`
section like so:

```
[ansible]
skip =
    2.9
    devel
```

This will avoid running tests with either of ansible-core 2.9 or devel.
