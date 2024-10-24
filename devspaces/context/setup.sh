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
    util-linux-user \
    which \
    zsh \
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

# Install oc client
OC_VERSION=4.15
curl -L https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable-${OC_VERSION}/openshift-client-linux.tar.gz | tar -C /usr/local/bin -xz --no-same-owner
chmod +x /usr/local/bin/oc
