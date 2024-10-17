#!/bin/bash
# cspell: ignore euxo chsh,iname
set -euxo pipefail

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# In OpenShift, container will run as a random uid number and gid 0. Make sure things
# are writeable by the root group.
for dir in \
    /tmp/dist \
    /home/runner \
    /home/runner/.ansible \
    /home/runner/.ansible/tmp \
    /runner \
    /home/runner \
    /runner/env \
    /runner/inventory \
    /runner/project \
    /runner/artifacts ; \
    do
    # shellcheck disable=SC2174
    mkdir -m 0775 -p $dir
    # do not use recursive (-R) because it will fail with read-only bind mounts
    find $dir -type d -exec chmod g+rwx {} \;
    find $dir -type f -exec chmod g+rw {} \;
    find $dir -exec chgrp root {} \;
done

for file in /home/runner/.ansible/galaxy_token /etc/passwd /etc/group; do
    touch $file
    chmod g+rw $file
    chgrp root $file;
done

# this must run as user root
find "$DIR/dist/" -iname '*.whl' -maxdepth 1 -exec python3 -m pip install --no-cache-dir '{}[server,lock]' \;

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
