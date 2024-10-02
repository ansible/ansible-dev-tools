#!/bin/bash -e
# cspell: ignore makecache overlayfs libssh chgrp
set -eux pipefail

set -e
dnf -y makecache
dnf -y update
dnf install -y \
    tar \
    podman \
    fuse-overlayfs \
    openssh-clients \
    zsh \
    util-linux-user \
    which \
    git \
    dumb-init \
    gcc \
    git-core \
    libssh-devel \
    python3-markupsafe \
    ncurses \
    python3-bcrypt \
    python3-cffi \
    python3-pip \
    python3-pyyaml \
    python3-ruamel-yaml \
    python3-wheel \
    --exclude container-selinux
dnf clean all

/usr/bin/python${PYV} -m pip install -r requirements.txt

ansible-galaxy collection install -r requirements.yml

chgrp -R 0 /home && chmod -R g=u /etc/passwd /etc/group /home

# Configure the podman wrapper
cp podman.py /usr/bin/podman.wrapper
chown 0:0 /usr/bin/podman.wrapper
chmod +x /usr/bin/podman.wrapper
