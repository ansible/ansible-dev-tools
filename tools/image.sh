#!/bin/bash -e
# cspell: ignore exuo,outdir
set -exuo pipefail

REPO_DIR=$(git rev-parse --show-toplevel)


# BUILD_CMD="podman build --squash-all"
BUILD_CMD="docker build --progress=plain"

python -m build --outdir "$REPO_DIR/final/dist/" --wheel "$REPO_DIR"
ansible-builder create -f execution-environment.yml --output-filename Containerfile -v3
$BUILD_CMD -f context/Containerfile context/ --tag community-ansible-dev-tools-base:latest
$BUILD_CMD -f final/Containerfile final/ --tag community-ansible-dev-tools:test
pytest --only-container --image-name community-ansible-dev-tools:test
