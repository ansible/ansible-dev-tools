---
hide:
  - navigation
  - toc
---

# Contributor Guide

To contribute to `ansible-dev-tools` python package or to the list of tools part of it, please use pull requests on a branch of your own fork.

After [creating your fork on GitHub], you can do:

```shell-session
$ git clone --recursive git@github.com:your-name/developer-tool-name
$ cd developer-tool-name
$ git checkout -b your-branch-name
# DO SOME CODING HERE
$ git add your new files
$ git commit -v
$ git push origin your-branch-name
```

You will then be able to create a pull request from your commit.

Prerequisites:

1. All fixes to core functionality (i.e. anything except docs or examples) should
   be accompanied by tests that fail prior to your change and succeed afterwards.

2. Before sending a PR, make sure that `tox -e lint` passes.

Feel free to raise issues in the repo if you feel unable to contribute a code
fix.

## Container testing

`pytest` has been extended to facilitate testing a container.

```shell
Custom options:
  --container-engine=CONTAINER_ENGINE
                        Container engine to use. (default=ADT_CONTAINER_ENGINE, podman, docker, '')
  --container-name=CONTAINER_NAME
                        Container name to use for the running container. (default=ADT_CONTAINER_NAME)
  --image-name=IMAGE_NAME
                        Container name to use. (default=ADT_IMAGE_NAME)
  --only-container      Only run container tests
  --include-container   Include container tests
```

Container tests can be run with either of the following commands:

```shell
# Run the tests against the default container engine
pytest --only-container
pytest --only-container --container-engine=<ce> --image-name <image>
tox -e test-image
tox -e test-image -- --container-engine=<ce> --image-name <image>
```

See the `tests/integration/test_container.py` for examples.

## Talk to us

- Join the Ansible forum:

  - [Get Help](https://forum.ansible.com/c/help/6): get help or help others. Please add appropriate tags if you start new discussions, for example the `devtools` tag.
  - [Posts tagged with 'devtools'](https://forum.ansible.com/tag/devtools): subscribe to participate in project-related conversations.
  - [Social Spaces](https://forum.ansible.com/c/chat/4): gather and interact with fellow enthusiasts.
  - [News & Announcements](https://forum.ansible.com/c/news/5): track project-wide announcements including social events.
  - [Bullhorn newsletter](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn): used to announce releases and important changes.

- We are also available on Matrix in the [#devtools:ansible.com](https://matrix.to/#/#devtools:ansible.com) room.

Possible security bugs should be reported via email to
<mailto:security@ansible.com>.

For more information about communication, see the [Ansible communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

## Code of Conduct

Please see the official [Ansible Community Code of Conduct].

[Ansible Community Code of Conduct]: https://docs.ansible.com/ansible/latest/community/code_of_conduct.html
[creating your fork on github]: https://docs.github.com/en/get-started/quickstart/contributing-to-projects
