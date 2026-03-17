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
    else
        echo "ERROR: Cannot resolve user and /etc/passwd is not writable" >&2
        exit 1
    fi
fi

USER=$(whoami)
CURRENT_UID=$(id -u)
START_ID=$(( CURRENT_UID + 1 ))

# Derive the available UID/GID range from the namespace mapping
# rather than assuming a fixed 65536 window.
if [ -r /proc/self/uid_map ]; then
    NAMESPACE_SIZE=$(awk '{print $3}' /proc/self/uid_map | head -n1)
else
    NAMESPACE_SIZE=65536
fi

END_ID=$(( NAMESPACE_SIZE - START_ID ))
if [ "${END_ID}" -le 0 ]; then
    echo "ERROR: No subordinate IDs available (uid=${CURRENT_UID}, namespace=${NAMESPACE_SIZE})" >&2
    exit 1
fi

echo "${USER}:${START_ID}:${END_ID}" >/etc/subuid
echo "${USER}:${START_ID}:${END_ID}" >/etc/subgid

exec /usr/libexec/podman/catatonit -- "$@"
