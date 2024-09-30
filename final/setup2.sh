#!/bin/bash
# cspell: ignore euxo chsh
set -euxo pipefail

# this must run as user root

mkdir -p ~/.ansible/roles /usr/share/ansible/roles /etc/ansible/roles
git config --system --add safe.directory /

# The dev container for docker runs as root
chsh -s "$(which zsh)" root

# Install argcomplete
python3 -m pip install argcomplete
activate-global-python-argcomplete

# Install oh-my-zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# add some helpful CLI commands to check we do not remove them inadvertently and output some helpful version information at build time.
set -ex
ansible --version
ansible-lint --version
ansible-runner --version
molecule --version
molecule drivers
podman --version
python3 --version
git --version
ansible-galaxy role list
ansible-galaxy collection list
rpm -qa
uname -a

# Make a workdir usable by the root user
mkdir -p /workdir
