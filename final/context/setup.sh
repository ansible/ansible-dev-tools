#!/bin/bash -e
# cspell: ignore onigurumacffi,makecache,euxo,libssh,overlayfs,setcaps
set -euxo pipefail

microdnf -q -y makecache
microdnf -q -y update
microdnf -q -y install shadow-utils
rpm --setcaps shadow-utils 2>/dev/null

microdnf remove -y subscription-manager dnf-plugin-subscription-manager
microdnf install -q -y \
tar \
echo \
podman \
fuse-overlayfs \
openssh-clients \
zsh \
util-linux-user \
which \
git \
nano \
vim \
dumb-init \
gcc \
git-core \
libssh-devel \
python3-markupsafe \
ncurses \
oniguruma-devel \
python3-bcrypt \
python3-cffi \
python3-devel \
python3-pip \
python3-pyyaml \
python3-ruamel-yaml \
python3-wheel \
--exclude container-selinux \
    && microdnf -q clean all \
    && ln -s /usr/bin/vim /usr/bin/vi
