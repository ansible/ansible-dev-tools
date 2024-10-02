#!/bin/bash -e
set -eux pipefail

if [[ -f "/usr/bin/apt-get" ]]; then
    sudo apt-get install -y -q libonig-dev
fi
