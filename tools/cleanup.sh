#!/bin/bash -e
# cspell: ignore exuo
set -exuo pipefail

sed -i '/GITHUB_TOKEN/d' .tox/*/log/*.log
