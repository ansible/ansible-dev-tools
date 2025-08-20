#!/bin/bash -e
# cspell: ignore euxo buildx execdir
set -euxo pipefail
ADT_CONTAINER_ENGINE=${ADT_CONTAINER_ENGINE:-docker}
IMAGE_NAME=ansible/ansible-workspace-env-reference:test

mkdir -p out dist
# Ensure that we packaged the code first
# shellcheck disable=SC2207
rm -f dist/*.*
tox -e pkg
# shellcheck disable=SC2207
WHEELS=($(find dist -name '*.whl' -maxdepth 1 -execdir echo '{}' ';'))
if [ ${#WHEELS[@]} -ne 1 ]; then
    echo "Unable to find a single wheel file in dist/ directory: ${WHEELS[*]}"
    exit 2
fi
rm -f devspaces/context/*.whl
ln -f dist/*.whl devspaces/context
ln -f tools/setup-image.sh devspaces/context

# we force use of linux/amd64 platform because source image supports only this
# platform and without it, it will fail to cross-build when task runs on arm64.
# --metadata-file=out/devspaces.meta --no-cache
$ADT_CONTAINER_ENGINE buildx build --tag=$IMAGE_NAME --platform=linux/amd64 devspaces/context -f devspaces/Containerfile

mk containers check $IMAGE_NAME --engine="${ADT_CONTAINER_ENGINE}" --max-size=1600 --max-layers=23

pytest --only-container --container-engine="${ADT_CONTAINER_ENGINE}" --container-name=devspaces --image-name=$IMAGE_NAME "$@" || echo "::error::Ignored failed devspaces tests, please https://github.com/ansible/ansible-dev-tools/issues/467"

if [[ -n "${GITHUB_SHA:-}" && "${GITHUB_EVENT_NAME:-}" != "pull_request" ]]; then
    $ADT_CONTAINER_ENGINE tag $IMAGE_NAME "ghcr.io/ansible/ansible-devspaces-tmp:${GITHUB_SHA}"
    # https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
    set +x  # Disable echo for lines with GITHUB_TOKEN
    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
    fi
    set -x
    $ADT_CONTAINER_ENGINE push "ghcr.io/ansible/ansible-devspaces-tmp:${GITHUB_SHA}"
fi
