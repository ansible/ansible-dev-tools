# Ansible Workspace Environment Reference Image for Openshift DevSpaces

An OpenShift Dev Spaces image specifically for Ansible development.

This comes pre-built with the [Ansible Development Tools](https://github.com/ansible/ansible-dev-tools) package.
For documentation on how to use these tools, please refer to [ADT docs](https://docs.ansible.com/projects/dev-tools/).

This image is built and published each time a new change is merged to the main
branch of ansible-dev-tools project. A release tag is created for each new
release of ansible-dev-tools project.

```bash
podman pull ghcr.io/ansible/ansible-devspaces:latest
```
