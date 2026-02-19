#!/bin/bash -e
# cspell: ignore exuo
set -exuo pipefail

if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac OSX sed
    sed -i '' '/GITHUB_TOKEN/d' .tox/*/log/*.log
else
    # GNU sed
    sed -i'' '/GITHUB_TOKEN/d' .tox/*/log/*.log
fi
