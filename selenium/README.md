# selenium-atd container

This container has selenium and vscode server in addition to 'adt' tools and
is used for testing vscode-ansible extension.

```bash
docker build -t {name} -f Dockerfile .
```

or

```bash
podman build -t {name} -f Dockerfile .
```

To run it:

```bash
docker run -it --shm-size=2g -p 4444:4444 -p 5999:5999 {name}
```

Alternatively, a pre built image can be pulled from quay:

```bash
docker run -it --shm-size=2g -p 4444:4444 -p 5999:5999 ghcr.io/ansible/selenium-adt
```

When the container starts, it will automatically start all the needed services.

You can connect to the container using a vnc client on port 5999 and see what
happens in the container the vs-code server runs on port 8080 and selenium runs
on port 4444
