#!/bin/bash -e
# cspell: ignore makecache overlayfs libssh chgrp noplugins
set -eux pipefail

set -e
dnf --noplugins remove -y -q subscription-manager dnf-plugin-subscription-manager
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
    "python${PYV}-markupsafe" \
    "python${PYV}-pip" \
    "python${PYV}-pyyaml" \
    "python${PYV}-wheel" \
    tar \
    tree \
    util-linux-user \
    which \
    zsh \
    --exclude container-selinux
#     python${PYV}-ruamel-yaml \
dnf -y -q clean all

"/usr/bin/python${PYV}" -m pip install --root-user-action=ignore -r requirements.txt

ansible-galaxy collection install -r requirements.yml

chgrp -R 0 /home && chmod -R g=u /etc/passwd /etc/group /home

# Configure the podman wrapper
cp podman.py /usr/bin/podman.wrapper
chown 0:0 /usr/bin/podman.wrapper
chmod +x /usr/bin/podman.wrapper
