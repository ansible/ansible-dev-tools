#!/bin/bash -e
# cspell: ignore onigurumacffi,makecache,euxo,libssh,overlayfs,setcaps,minrate,openh264
set -euxo pipefail

# When building for multiple-architectures in parallel using emulation
# it's really easy for one/more dnf processes to timeout or mis-count
# the minimum download rates.  Bump both to be extremely forgiving of
# an overworked host.
echo -e "\n\n# Added during image build" >> /etc/dnf/dnf.conf
echo -e "minrate=100\ntimeout=60\n" >> /etc/dnf/dnf.conf
#  might config-manager is not available
# microdnf config-manager --disable fedora-cisco-openh264
rm -f /etc/yum.repos.d/fedora-cisco-openh264.repo

microdnf -q -y makecache && microdnf -q -y update
microdnf -q -y install shadow-utils
rpm --setcaps shadow-utils 2>/dev/null

microdnf remove -y subscription-manager dnf-plugin-subscription-manager

# gcc: for ansible-pylibssh, onigurumacffi/arm64
# ncurses: for ansible-navigator
# oniguruma-devel: onigurumacffi/arm64 (does not have binary)
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
