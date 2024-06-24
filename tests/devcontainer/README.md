# RPM and container testing

1. Install [task](https://taskfile.dev/installation/)
2. Run `task build` to build the container and .devcontainer file
3. Make sure you have the MS devcontainers extension installed
4. Reopen the workspace in the container CTRL-SHIFT-P -> Reopen inside container
5. Run `task -t Taskfile.test.yml` to test the container in the container.

Please take note of the task descriptions and summaries. Although the tasks pass,
some are negative tests showing an issue.
