#!/bin/bash -e
# cspell: ignore euxo buildx
set -euxo pipefail
ADT_CONTAINER_ENGINE=${ADT_CONTAINER_ENGINE:-docker}
CONTAINER_NAME=ansible/ansible-workspace-env-reference:test
env

mkdir -p out
# we force use of linux/amd64 platform because source image supports only this
# platform and without it, it will fail to cross-build when task runs on arm64.
# --metadata-file=out/devspaces.meta --no-cache
$ADT_CONTAINER_ENGINE buildx build --tag=$CONTAINER_NAME --platform=linux/amd64 devspaces/context -f devspaces/Containerfile

mk containers check $CONTAINER_NAME --engine="${ADT_CONTAINER_ENGINE}" --max-size=1600 --max-layers=23

if [[ -n "${GITHUB_SHA:-}" ]]; then
    $ADT_CONTAINER_ENGINE tag $CONTAINER_NAME "ghcr.io/ansible/ansible-devspaces-tmp:${GITHUB_SHA}"
    # https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
    fi
    $ADT_CONTAINER_ENGINE push "ghcr.io/ansible/ansible-devspaces-tmp:${GITHUB_SHA}"
fi
