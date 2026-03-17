#!/bin/bash -e
# cspell: ignore makecache overlayfs libssh chgrp noplugins newuidmap newgidmap subuid subgid
set -eux pipefail

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

dnf --noplugins remove -y -q subscription-manager dnf-plugin-subscription-manager iptables-legacy
dnf install -y -q iptables-nft
dnf -y -q makecache
dnf -y -q update
dnf install -y -q \
    buildah \
    crun \
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
    skopeo \
    tar \
    util-linux-user \
    which \
    zsh \
    pinentry \
    --exclude container-selinux
dnf -y -q clean all

# Set python3/pip3 alternatives so they work with or without version suffix
alternatives --install /usr/bin/python3 python3 "/usr/bin/python${PYV}" 100
alternatives --set python3 "/usr/bin/python${PYV}"
alternatives --install /usr/bin/pip3 pip3 "/usr/bin/pip${PYV}" 100
alternatives --set pip3 "/usr/bin/pip${PYV}"

"/usr/bin/python${PYV}" -m pip install --only-binary :all: --root-user-action=ignore "$(ls -1 ./*.whl)[server]" -r requirements.txt

ansible-galaxy collection install -r requirements.yml

# Setup for rootless podman with user namespaces (container-in-container)
setcap cap_setuid+ep /usr/bin/newuidmap
setcap cap_setgid+ep /usr/bin/newgidmap
touch /etc/subgid /etc/subuid
chown 0:0 /etc/subgid /etc/subuid

chgrp -R 0 /home && chmod -R g=u /etc/passwd /etc/group /etc/subuid /etc/subgid /home

# Install the colored bash prompt
cp ansible-prompt.sh /etc/profile.d/ansible-prompt.sh
chmod +r /etc/profile.d/ansible-prompt.sh

# Install the entrypoint for rootless podman UID mapping
cp entrypoint.sh /entrypoint.sh
chmod +x /entrypoint.sh

# shellcheck disable=SC1091
source "$DIR/setup-image.sh"
