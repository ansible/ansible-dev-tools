#!/bin/bash -e
# cspell: ignore onigurumacffi,makecache,euxo,libssh,overlayfs,setcaps,minrate,openh264,additionalimage,mountopt,nodev,iname,chsh,PIND
set -euxo pipefail

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
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
--exclude container-selinux

microdnf -q clean all
ln -s /usr/bin/vim /usr/bin/vi

curl -o /etc/containers/containers.conf https://raw.githubusercontent.com/containers/image_build/main/podman/containers.conf
chmod 644 /etc/containers/containers.conf

# Copy & modify the defaults to provide reference if runtime changes needed.
# Changes here are required for running with fuse-overlay storage inside container.
sed -e 's|^#mount_program|mount_program|g' \
    -e '/additionalimage.*/a "/var/lib/shared",' \
    -e 's|^mountopt[[:space:]]*=.*$|mountopt = "nodev,fsync=0"|g' \
    /usr/share/containers/storage.conf \
    > /etc/containers/storage.conf

# Apparently, PIND on MacOS fails to build containers when drive=overlayfs but works with vfs!
sed -i -e 's|^driver =.*$|driver = "vfs"|g' /etc/containers/storage.conf

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p /var/lib/shared/overlay-images /var/lib/shared/overlay-layers /var/lib/shared/vfs-images /var/lib/shared/vfs-layers
touch /var/lib/shared/overlay-images/images.lock /var/lib/shared/overlay-layers/layers.lock /var/lib/shared/vfs-images/images.lock /var/lib/shared/vfs-layers/layers.lock

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
find "$DIR/dist/" -iname '*.whl' -maxdepth 1 -exec python3 -m pip install --no-cache-dir '{}[server]' \;

mkdir -p ~/.ansible/roles /usr/share/ansible/roles /etc/ansible/roles
git config --system --add safe.directory /

# The dev container for docker runs as root
chsh -s "$(which zsh)" root

# Install argcomplete
python3 -m pip install argcomplete
activate-global-python-argcomplete

# shellcheck disable=SC1091
source "$DIR/setup-image.sh"

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

# compatibility with recent docker versions:
chmod go+rwx /etc/passwd
