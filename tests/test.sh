echo "::group::Starting tests"

set -ex

cd /home/podman/tests

adt --version

podman run hello

ansible-navigator run site.yml --mode stdout

echo "::endgroup::"
