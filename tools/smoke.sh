#!/bin/bash -e
# cspell: disable chectl spodwaittimeout USERSTORY mmusiien OAUTH
set -eu pipefail

NC='\033[0m' # No Color
export DEBIAN_FRONTEND=noninteractive
# Use "log [notice|warning|error] message" to  print a colored message to
# stderr, with colors.
log () {
    local prefix
    if [ "$#" -ne 2 ]; then
        log error "Incorrect call ($*), use: log [group|notice|warning|error] 'message'."
        exit 2
    fi
    case $1 in
        group)
            if [ -n "${GITHUB_ACTIONS:-}" ]; then
                prefix='::endgroup::\n::group::GROUP\n\033[0;36mGROUP:  '
            else
                prefix='\033[0;36mGROUP:  '
            fi
            ;;
        notice) prefix='\033[0;36mNOTICE:  ' ;;
        warning) prefix='\033[0;33mWARNING: ' ;;
        error) prefix='\033[0;31mERROR:   ' ;;
        *)
        log error "log first argument must be 'notice', 'warning' or 'error', not $1."
        exit 2
        ;;
    esac
    echo >&2 -e "${prefix}${2}${NC}"
}

log group "Running smoke.sh"

ARCH=$(arch)
if [ "$ARCH" == "aarch64" ] || [ "$ARCH" == "arm64" ]; then
    ARCH="arm64"
    log error "Unsupported architecture: $ARCH"
    exit 1
elif [ "$ARCH" == "x86_64" ]; then
    ARCH="amd64"
else
    log error "Unsupported architecture: $ARCH"
    exit 1
fi

if [[ -f "/usr/bin/apt-get" ]]; then
    sudo apt-get update -y -qq
    sudo apt-get install -y -qq libonig-dev tox podman-docker

    # https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-using-native-package-management
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list   # helps tools such as command-not-found to work correctly
    sudo apt-get update -qq
    sudo apt-get install -y -q kubectl

    type minikube 2>/dev/null || {
        curl -s -o /tmp/minikube_latest.deb https://storage.googleapis.com/minikube/releases/latest/minikube_latest_$ARCH.deb
        sudo dpkg -i /tmp/minikube_latest.deb
    }
    minikube version
    log group "Running minikube start"
    minikube start
fi

# not supporting aarch64 architecture!
log group "Install chectl"
bash <(curl -sL https://che-incubator.github.io/chectl/install.sh) --channel=next

log group "Deploy Che"
#
# load che-code images from /tmp/che-code-latest.tar
#
eval "$(minikube docker-env)" && docker load -i  /tmp/che-code-latest.tar && rm /tmp/che-code-latest.tar

#
# deploy Che
#
chectl server:deploy \
--batch \
--platform minikube \
--k8spodwaittimeout=480000 \
--k8spodreadytimeout=480000
# --che-operator-cr-patch-yaml "${GITHUB_WORKSPACE}/build/test/github-minikube-checluster-patch.yaml"

#
# apply patch
#
# kubectl patch devworkspaceoperatorconfigs \
#   -n eclipse-che devworkspace-config \
#   --patch '{"config": {"workspace": {"imagePullPolicy": "IfNotPresent"}}}' \
#   --type merge

log group "Pull Universal Base Image"
minikube image pull ghcr.io/ansible/ansible-devspaces:latest


log group "Run smoke test"
docker run \
    --shm-size=2048m \
    -p 5920:5920 \
    --network="host" \
    -e TS_SELENIUM_LOAD_PAGE_TIMEOUT=60000 \
    -e TS_SELENIUM_USERNAME=che@eclipse.org \
    -e TS_SELENIUM_PASSWORD=admin \
    -e TS_SELENIUM_BASE_URL="https://$(kubectl get ingress che -n eclipse-che -o jsonpath='{.spec.rules[0].host}')" \
    -e DELETE_WORKSPACE_ON_FAILED_TEST=true \
    -e TS_SELENIUM_START_WORKSPACE_TIMEOUT=120000 \
    -e NODE_TLS_REJECT_UNAUTHORIZED=0 \
    -e VIDEO_RECORDING=true \
    -e TS_SELENIUM_LOG_LEVEL=TRACE \
    -e TS_WAIT_LOADER_PRESENCE_TIMEOUT=120000 \
    -e TS_COMMON_DASHBOARD_WAIT_TIMEOUT=30000 \
    -e USERSTORY=SmokeTest \
    -e TS_SELENIUM_VALUE_OPENSHIFT_OAUTH=false \
    -e TEST_REPO=https://raw.githubusercontent.com/ansible/ansible-dev-tools/refs/heads/main/devfile.yaml \
    quay.io/mmusiien/che-e2e:smoke-test

    # -v ${LOCAL_TEST_DIR}/tests/e2e/report:/tmp/e2e/report:Z \
    # -v ${LOCAL_TEST_DIR}/tests/e2e/video:/tmp/ffmpeg_report:Z \
