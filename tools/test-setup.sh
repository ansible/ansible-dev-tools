#!/bin/bash -e
# cspell: ignore hhvm anthoscli
set -eux pipefail

if [[ -f "/usr/bin/apt-get" ]]; then
    dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n | tail -n 20
    df -h
    echo "Removing large packages so GHA runners do not run out of disk space during image building"
    sudo apt-get remove -y '^ghc-8.*' '^dotnet-.*' '^llvm-.*' 'php.*' azure-cli google-cloud-sdk hhvm google-chrome-stable google-cloud-cli google-cloud-cli-anthoscli firefox powershell mono-devel microsoft-edge-stable || true
    sudo apt-get autoremove -y
    sudo apt-get install -y -q libonig-dev
    sudo apt-get clean
    sudo rm -rf /usr/share/dotnet/
    df -h
    podman info --format '{{ json .Store }}' | jq
    podman system df
fi
