#!/bin/bash -e
# Script that is used to install the necessary dependencies for both container
# images, devspaces and ee.
# cspell: ignore exuo
set -exuo pipefail

# Install oc client
OC_VERSION=4.15
curl -s -L "https://mirror.openshift.com/pub/openshift-v4/$(arch)/clients/ocp/stable-${OC_VERSION}/openshift-client-linux.tar.gz" | tar -C /usr/local/bin -xz --no-same-owner
chmod +x /usr/local/bin/oc
oc version --client=true

# Ensure that we have a ~/.zshrc file as otherwise zsh will start its first run
# wizard which will cause the container to hang. This was seen as happening on
# ubi9 image but not on fedora one.
touch ~/.zshrc

# Install oh-my-zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
