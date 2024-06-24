 podman run -it --rm  \
 --cap-add=SYS_ADMIN \
 --cap-add=SYS_RESOURCE \
 --device "/dev/fuse" \
 --hostname=ansible-dev-container \
 --name=ansible-dev-container-downstream \
 --security-opt "apparmor=unconfined" \
 --security-opt "label=disable" \
 --security-opt "seccomp=unconfined" \
 --user=root \
 --userns=host \
 -e SSH_AUTH_SOCK=$SSH_AUTH_SOCK \
 -v ansible-dev-tools-container-storage:/var/lib/containers \
 -v $HOME/.gitconfig:/root/.gitconfig \
 -v $PWD:/workdir \
 -v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK \
   brew.registry.redhat.io/rh-osbs/ansible-automation-platform-25-ansible-dev-tools-rhel8:24.5.0-1
