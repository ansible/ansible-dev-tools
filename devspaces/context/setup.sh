#!/bin/bash -e
# cspell: ignore makecache overlayfs libssh chgrp noplugins
set -eux pipefail

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

dnf --noplugins remove -y -q subscription-manager dnf-plugin-subscription-manager iptables-legacy
dnf install -y -q iptables-nft
dnf -y -q makecache
dnf -y -q update
dnf install -y -q \
    dumb-init \
    fuse-overlayfs \
    gcc \
    git \
    git-core \
    libssh-devel \
    ncurses \
    openssh-clients \
    podman \
    "python${PYV}" \
    "python${PYV}-cffi" \
    "python${PYV}-pip" \
    "python${PYV}-pyyaml" \
    "python${PYV}-wheel" \
    tar \
    util-linux-user \
    which \
    zsh \
    pinentry \
    --exclude container-selinux
#     python${PYV}-ruamel-yaml \
dnf -y -q clean all

"/usr/bin/python${PYV}" -m pip install --root-user-action=ignore "$(ls -1 ./*.whl)[server,lock]" -r requirements.txt

ansible-galaxy collection install -r requirements.yml

chgrp -R 0 /home && chmod -R g=u /etc/passwd /etc/group /home

# Configure the podman wrapper
cp podman.py /usr/bin/podman.wrapper
chown 0:0 /usr/bin/podman.wrapper
chmod +x /usr/bin/podman.wrapper

# shellcheck disable=SC1091
source "$DIR/setup-image.sh"
