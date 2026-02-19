#!/bin/bash -e
# cspell: ignore exuo,outdir,aarch64,iname,buildx
set -exuo pipefail


ADT_CONTAINER_ENGINE=${ADT_CONTAINER_ENGINE:-docker}

# Identify the architecture in format used by the container engines because
# `arch` command returns either arm64 or aarch64 depending on the system
ARCH=$(arch)
if [ "$ARCH" == "aarch64" ] || [ "$ARCH" == "arm64" ]; then
    ARCH="arm64"
elif [ "$ARCH" == "x86_64" ]; then
    ARCH="amd64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi


# keep the localhost/ prefix on image name all the time or we will face various
# problems related to docker/podman differences when this is missing.
IMAGE_NAME=localhost/selenium-adt:test

# BUILD_CMD="podman build --squash-all"
BUILD_CMD="${ADT_CONTAINER_ENGINE} buildx build --progress=plain"

# Publish should run on CI only on main branch, with or without release tag
if [ "--publish" == "${1:-}" ]; then
    if [ -z "${2:-}" ]; then
        echo "Please also pass the tag to be published for the merged image. Source image will use the sha tag."
        exit 1
    fi

    set +x  # Disable echo for lines with GITHUB_TOKEN
    if [ -n "${GITHUB_TOKEN:-}" ] && [ -n "${GITHUB_ACTOR:-}" ]; then
        echo "${GITHUB_TOKEN:-}" | ${ADT_CONTAINER_ENGINE} login ghcr.io -u "${GITHUB_ACTOR:-}" --password-stdin
    fi
    set -x
    if [ -z "${GITHUB_SHA:-}" ]; then
        echo "Unable to find GITHUB_SHA variable."
        exit 1
    fi
    ${ADT_CONTAINER_ENGINE} pull -q "ghcr.io/ansible/selenium-adt-tmp:${GITHUB_SHA:-}-arm64"
    ${ADT_CONTAINER_ENGINE} pull -q "ghcr.io/ansible/selenium-adt-tmp:${GITHUB_SHA:-}-amd64"

    for TAG in ghcr.io/ansible/selenium-adt:${2:-} ghcr.io/ansible/selenium-adt:latest; do
        ${ADT_CONTAINER_ENGINE} manifest create "$TAG" --amend "ghcr.io/ansible/selenium-adt-tmp:${GITHUB_SHA:-}-amd64" --amend "ghcr.io/ansible/selenium-adt-tmp:${GITHUB_SHA:-}-arm64"
        ${ADT_CONTAINER_ENGINE} manifest annotate --arch arm64 "$TAG" "ghcr.io/ansible/selenium-adt-tmp:${GITHUB_SHA:-}-arm64"

        # We push only when there is a release, and that is when $2 is not the same as GITHUB_SHA
        if [ "--dry" != "${3:-}" ]; then
            ${ADT_CONTAINER_ENGINE} manifest push "$TAG"
        fi
    done
    exit 0
fi

$BUILD_CMD -f selenium/Containerfile selenium/ --tag "${IMAGE_NAME}"

if [[ -n "${GITHUB_SHA:-}" && "${GITHUB_EVENT_NAME:-}" != "pull_request" ]]; then
    FQ_IMAGE_NAME="ghcr.io/ansible/selenium-adt-tmp:${GITHUB_SHA}-$ARCH"
    $ADT_CONTAINER_ENGINE tag $IMAGE_NAME "${FQ_IMAGE_NAME}"
    # https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
    set +x  # Disable echo for lines with GITHUB_TOKEN
    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
    fi
    set -x
    $ADT_CONTAINER_ENGINE push "${FQ_IMAGE_NAME}"
fi
