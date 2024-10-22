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
