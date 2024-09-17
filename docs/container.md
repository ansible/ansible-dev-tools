# community-ansible-dev-tools

A container image for Ansible Development Tools (ADT).

This image is built on top of [Fedora minimal](https://quay.io/repository/fedora/fedora-minimal?tab=info) and has container-in-container support with [`podman`](https://podman.io/docs).

The current version in use can be found in the [`execution-environment.yml`](https://github.com/ansible/ansible-dev-tools/blob/main/execution-environment.yml) file used for the base layer.

## Installation

```bash
podman pull ghcr.io/ansible/community-ansible-dev-tools:latest
```

## Usage

### Using this as a VS code Dev Container

Dev Containers provide you with a containerized development environment in VS code. Details on what they are and how to use them can be found in [Developing inside a Container](https://code.visualstudio.com/docs/devcontainers/containers).

This image can be used as an image for a Dev Container where you build and consume Ansible content.

This repository comes with a sample [`.devcontainer directory`](https://github.com/ansible/ansible-dev-tools/tree/main/.devcontainer) with 2 subdirectories - `podman` and `docker` each having its own
`devcontainer.json` file.

You can simply copy over the `.devcontainer` directory to your Ansible project and start using it!

### Using this with Github Codespaces

To use this image with [Github Codespaces](https://docs.github.com/en/codespaces/overview), copy the [`devcontainer.json`](https://github.com/ansible/ansible-dev-tools/blob/main/.devcontainer/devcontainer.json) in this repo to your project and push to Github.

**Note:** If you are planning to start writing a new Ansible playbook project or collection, use [Ansible Creator](https://ansible.readthedocs.io/projects/creator) to scaffold it for you and your project/collection will already have all the `.devcontainer` files ready.

### Using this image as an EE

This image can also be used as an Ansible Execution Environment (EE). If you're not familiar with what an EE is, checkout the documentation in [Getting started with EE](https://docs.ansible.com/ansible/devel/getting_started_ee/index.html). It is shipped with the following Ansible collections:

- ansible.netcommon
- ansible.posix
- ansible.scm
- ansible.utils

You can also create a new EE based on this with more Ansible collections (or Python/System packages) of your choice by using Ansible Builder. Read this [documentation](https://ansible.readthedocs.io/projects/builder/en/latest/) to know about ansible-builder.

The below example shows how to make a custom EE that adds the `amazon.aws` and `cisco.nxos` collections as well as the `ansible-pylibssh` python package to this image.

1. Create an `execution-environment.yml` file with the following content.

   ```yaml title="execution-environment.yml"
   ---
   version: 3

   images:
     base_image: ghcr.io/ansible/community-ansible-dev-tools-container:latest

   dependencies:
     galaxy: requirements.yml
     python: requirements.txt
   ```

2. Populate `requirements.txt` and `requirements.yml` with the respective contents.

   ```text title="requirements.txt"
   ansible-pylibssh==1.1.0
   ```

   ```yaml title="requirements.yml"
   ---
   collections:
     - name: amazon.aws
     - name: cisco.nxos
   ```

3. Use `ansible-builder` to create the new EE.

   ```bash
   ansible-builder build -t custom-ee:latest --prune-images -v3
   ```

Once this image is built, you can use [`ansible-navigator`](https://ansible.readthedocs.io/projects/navigator/) to reference this image and run your playbooks!

### Using with podman from the command-line

If you want to use this image with `podman` the following command to run the container.

```bash
podman run  -it --rm \
 --cap-add=SYS_ADMIN \
 --cap-add=SYS_RESOURCE \
 --device "/dev/fuse" \
 --hostname=ansible-dev-container \
 --name=ansible-dev-container \
 --security-opt "apparmor=unconfined" \
 --security-opt "label=disable" \
 --security-opt "seccomp=unconfined" \
 --user=root \
 --userns=host \
 -e SSH_AUTH_SOCK=$SSH_AUTH_SOCK \
 -v $HOME/.gitconfig:/root/.gitconfig \
 -v $PWD:/workdir \
 -v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK \
 ghcr.io/ansible/community-ansible-dev-tools:latest
```

Note:

- The `security-opt` and `cap-add` options are used to allow `podman` to run in the container.
- The `device` option is used to allow the container to access the `/dev/fuse` device.
- `userns=host` maps the default user account to root user in container.
- This command will mount the current directory to `/workdir` in the container
- The SSH agent socket is also mounted to the container to allow for SSH key forwarding.
- The user's `.gitconfig` is mounted to the container to allow for git operations.

### Signing git commits (SSH)

If the `user.signingkey` in the `gitconfig` points directly public key on the file system that key may not be available in the container.

If only one key is preset, the `ssh-add` command can be used for key retrieval in the user's `gitconfig`:

```toml title="~/.gitconfig"
[gpg "ssh"]
    defaultKeyCommand = ssh-add -L
```

Alternatively, the public key can added in-line in the `gitconfig`

```toml title="~/.gitconfig"
[user]
  email = johnd@acme.com
  name = John Doe
  signingkey = key:: ssh-rsa ...
```

### Layering ADT and container-in-container support on a custom image

To add the Ansible Devtools package and the container-in-container support with podman using a custom EE or another container image, you can use to the [final
Containerfile](https://github.com/ansible/ansible-dev-tools/blob/main/final/Containerfile) from this repository. Update the `FROM` instruction to point to
your preferred image and build it using `podman` or `docker`.

**Note:** The container-in-container support is added with the help of the [podman image](https://github.com/containers/image_build/tree/main/podman) definition. For more information, read [How to use Podman inside of a container](https://www.redhat.com/sysadmin/podman-inside-container).

## Related Links

- [ansible-builder](https://github.com/ansible/ansible-builder)
- [ansible-creator](https://github.com/ansible/ansible-creator)
- [podman](https://github.com/containers/podman/)
