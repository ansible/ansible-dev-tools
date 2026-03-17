#!/usr/bin/env bash
# Entrypoint for the Ansible Dev Spaces container image.
# Sets up the dynamic UID mapping required for rootless podman
# with user namespaces (container-in-container without kubedock).
# cspell: ignore subuid subgid catatonit

if [ ! -d "${HOME}" ]; then
    mkdir -p "${HOME}"
fi

if ! whoami &>/dev/null; then
    if [ -w /etc/passwd ]; then
        echo "${USER_NAME:-user}:x:$(id -u):0:${USER_NAME:-user} user:${HOME}:/bin/bash" >>/etc/passwd
        echo "${USER_NAME:-user}:x:$(id -u):" >>/etc/group
    fi
fi

USER=$(whoami)
START_ID=$(( $(id -u) + 1 ))
END_ID=$(( 65536 - START_ID ))
echo "${USER}:${START_ID}:${END_ID}" >/etc/subuid
echo "${USER}:${START_ID}:${END_ID}" >/etc/subgid

exec /usr/libexec/podman/catatonit -- "$@"
