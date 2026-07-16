#!/bin/bash -e
# cspell: ignore exuo,outdir,aarch64,iname,buildx
set -exuo pipefail


ADT_CONTAINER_ENGINE=${ADT_CONTAINER_ENGINE:-docker}
# When set to 1, final image overlays ADT ecosystem packages from each repo's
# default-branch tip (see final/setup.sh / final/from-main-requirements.txt) and
# uses a distinct tmp tag suffix to avoid colliding with the default :main build
# for the same commit SHA.
ADT_IMAGE_FROM_MAIN="${ADT_IMAGE_FROM_MAIN:-0}"
TMP_TAG_SUFFIX=""
if [ "${ADT_IMAGE_FROM_MAIN}" = "1" ]; then
    TMP_TAG_SUFFIX="-from-main"
fi

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

REPO_DIR=$(git rev-parse --show-toplevel)

TAG_BASE=community-ansible-dev-tools-base:latest
# keep the localhost/ prefix on image name all the time or we will face various
# problems related to docker/podman differences when this is missing.
IMAGE_NAME=localhost/community-ansible-dev-tools:test

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

    FINAL_REPO="ghcr.io/ansible/community-ansible-dev-tools"
    TMP_REPO="ghcr.io/ansible/community-ansible-dev-tools-tmp"
    SHA_TAG="${GITHUB_SHA:-}${TMP_TAG_SUFFIX}"

    ${ADT_CONTAINER_ENGINE} pull -q "${TMP_REPO}:${SHA_TAG}-arm64"
    ${ADT_CONTAINER_ENGINE} pull -q "${TMP_REPO}:${SHA_TAG}-amd64"

    # Re-tag and push arch-specific images to the final repository to avoid
    # cross-repository blob mounting issues when creating the manifest.
    # GHCR cannot mount blobs across different repositories, so we must push
    # the images to the target repository before creating the manifest.
    for IMG_ARCH in amd64 arm64; do
        ${ADT_CONTAINER_ENGINE} tag "${TMP_REPO}:${SHA_TAG}-${IMG_ARCH}" "${FINAL_REPO}:${SHA_TAG}-${IMG_ARCH}"
        if [ "${CI:-}" == "true" ]; then
            ${ADT_CONTAINER_ENGINE} push "${FINAL_REPO}:${SHA_TAG}-${IMG_ARCH}"
        fi
    done

    TAGS=("${FINAL_REPO}:${2:-}")
    if [ -n "${3:-}" ]; then
        TAGS+=("${FINAL_REPO}:${3}")
    fi

    for TAG in "${TAGS[@]}"; do
        ${ADT_CONTAINER_ENGINE} manifest create "$TAG" --amend "${FINAL_REPO}:${SHA_TAG}-amd64" --amend "${FINAL_REPO}:${SHA_TAG}-arm64"
        ${ADT_CONTAINER_ENGINE} manifest annotate --arch arm64 "$TAG" "${FINAL_REPO}:${SHA_TAG}-arm64"

        if [ "${CI:-}" == "true" ]; then
            ${ADT_CONTAINER_ENGINE} manifest push "$TAG"
        fi
    done
    exit 0
fi

# Code for building the container (call script again with --publish to merge and push already build container)

# Self-hosted builders keep docker/podman cache across jobs; leftover layers
# have been causing out-of-disk errors in nested ansible-builder (test_builder).
if [ "${CI:-}" = "true" ]; then
    df -h || true
    ${ADT_CONTAINER_ENGINE} system prune -af --volumes || true
    ${ADT_CONTAINER_ENGINE} builder prune -af || true
    df -h || true
fi

if [ -d "$REPO_DIR/final/dist/" ]; then
    find "$REPO_DIR/final/dist/" -type f -delete
fi
python -m build --outdir "$REPO_DIR/final/dist/" --wheel "$REPO_DIR"
ansible-builder create -f execution-environment.yml --output-filename Containerfile -v3
$BUILD_CMD -f context/Containerfile context/ --tag "${TAG_BASE}"
ln -f tools/setup-image.sh final/
$BUILD_CMD \
    --build-arg "ADT_IMAGE_FROM_MAIN=${ADT_IMAGE_FROM_MAIN}" \
    -f final/Containerfile final/ --tag "${IMAGE_NAME}"

# We save local image in order to import it inside the container later for c-in-c testing
# Do not try to gzip the image because there is no notable change in size and
# it seems to add ~20% more in total test execution time.
$ADT_CONTAINER_ENGINE save $IMAGE_NAME > image.tar

# Drop intermediate base/build cache before nested EE builds; keep the test image.
${ADT_CONTAINER_ENGINE} rmi "${TAG_BASE}" || true
${ADT_CONTAINER_ENGINE} builder prune -af || true
${ADT_CONTAINER_ENGINE} image prune -f || true
df -h || true

pytest -v src/ansible_dev_tools/tests --include-container --container-engine="${ADT_CONTAINER_ENGINE}" --image-name "${IMAGE_NAME}"
# Test the build of example execution environment to avoid regressions
pushd docs/examples
ansible-builder build --container-runtime="${ADT_CONTAINER_ENGINE}"
popd

if [[ -n "${GITHUB_SHA:-}" && "${GITHUB_EVENT_NAME:-}" != "pull_request" ]]; then
    FQ_IMAGE_NAME="ghcr.io/ansible/community-ansible-dev-tools-tmp:${GITHUB_SHA}${TMP_TAG_SUFFIX}-$ARCH"
    $ADT_CONTAINER_ENGINE tag $IMAGE_NAME "${FQ_IMAGE_NAME}"
    # https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
    set +x  # Disable echo for lines with GITHUB_TOKEN
    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
    fi
    set -x
    $ADT_CONTAINER_ENGINE push "${FQ_IMAGE_NAME}"
fi
