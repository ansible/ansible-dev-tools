"""A forum poster."""

import argparse
import datetime
import json
import urllib.request

from urllib.request import Request


POST_MD = """Hello everyone,

We are happy to announce the release of {project} {release}.

# How to get it

You can install the latest version of all the ansible developer tools by running the following command:

```bash
python3 -m pip -U install ansible-dev-tools
```

This will install the following developer tools:

- [ansible-builder](https://ansible.readthedocs.io/projects/builder/): Ansible Builder automates the process of building execution environments using the schemas and tooling defined in various Ansible Collections and by the user.
- [ansible-core](https://ansible.readthedocs.io/projects/ansible/): Ansible is a radically simple IT automation platform that makes your applications and systems easier to deploy and maintain. Automate everything from code deployment to network configuration to cloud management, in a language that approaches plain English, using SSH, with no agents to install on remote systems.
- [ansible-creator](https://ansible.readthedocs.io/projects/creator/): The fastest way to generate all your ansible content!
- [ansible-dev-environment](https://ansible.readthedocs.io/projects/dev-environment/): A pip-like install for Ansible collections.
- [ansible-lint](https://ansible.readthedocs.io/projects/lint/): Checks playbooks for practices and behavior that could potentially be improved.
- [ansible-navigator](https://ansible.readthedocs.io/projects/navigator/) A text-based user interface (TUI) for Ansible.
- [ansible-sign](https://ansible.readthedocs.io/projects/sign/): Utility for signing and verifying Ansible project directory contents.
- [molecule](https://ansible.readthedocs.io/projects/molecule/): Molecule aids in the development and testing of Ansible content: collections, playbooks and roles
- [pytest-ansible](https://ansible.readthedocs.io/projects/pytest-ansible/): A pytest plugin that enables the use of ansible in tests, enables the use of pytest as a collection unit test runner, and exposes molecule scenarios using a pytest fixture.
- [tox-ansible](https://ansible.readthedocs.io/projects/tox-ansible/): The tox-ansible plugin dynamically creates a full matrix of python interpreter and ansible-core version environments for running integration, sanity, and unit for an ansible collection both locally and in a Github action. tox virtual environments are leveraged for collection building, collection installation, dependency installation, and testing.

For a single tool, you can install it by running:

```bash
python3 -m pip -U install <project>==<release>
```

All ansible developer tools are also packaged in an image that you can use as a [VsCode development container](https://code.visualstudio.com/docs/devcontainers/containers). The image is updated shortly after releases of any individual tool.
The [community-dev-tools](https://github.com/ansible/ansible-dev-tools/pkgs/container/community-ansible-dev-tools) image is available on GitHub Container Registry.

```
podman run -it ghcr.io/ansible/community-ansible-dev-tools:latest
```

Sample `devcontainer.json` files are available in the [ansible-dev-tools](https://github.com/ansible/ansible-dev-tools/tree/main/.devcontainer) repository.

# Release notes for {project} {release}

{release_notes}

Release notes for all versions can be found in the [changelog](https://github.com/ansible/{project}/releases).

"""  # noqa: E501


class Post:
    """A class to post a release on the Ansible forum."""

    def __init__(self, project: str, release: str, forum_api_key: str, forum_user: str) -> None:
        """Initialize the Post class.

        Args:
            project: The project name.
            release: The release version.
            forum_api_key: The forum API key.
            forum_user: The forum user.
        """
        self.category_id: int
        self.created: str
        self.forum_api_key = forum_api_key
        self.forum_user = forum_user
        self.project = project
        self.release = release
        self.release_notes: str
        self.user = "ansible-announce"

    def _get_release_notes(self) -> None:
        """Get the release notes for the project."""
        release_url = (
            f"https://api.github.com/repos/ansible/{self.project}/releases/tags/{self.release}"
        )
        with urllib.request.urlopen(release_url) as url:  # noqa: S310
            data = json.load(url)
        self.release_notes = data["body"]
        self.created = data["created_at"]

    def _get_category_id(self) -> None:
        """Get the category ID for the project."""
        categories_url = "https://forum.ansible.com/categories.json"
        categories_request = Request(categories_url)  # noqa: S310
        categories_request.add_header("Api-Key", self.forum_api_key)
        categories_request.add_header("Api-Username", self.forum_user)
        with urllib.request.urlopen(url=categories_request) as url:  # noqa: S310
            data = json.load(url)
        self.category_id = next(
            c for c in data["category_list"]["categories"] if c["name"] == "Sandbox"
        )["id"]

    def post(self) -> None:
        """Post the release announcement to the forum."""
        self._get_release_notes()
        self._get_category_id()
        post_md = POST_MD.format(
            project=self.project,
            release=self.release,
            release_notes=self.release_notes,
        )
        now = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        title = f"Release Announcement: {self.project} {self.release}"

        payload = {
            "title": title,
            "raw": post_md,
            "category": self.category_id,
            "created_at": self.created,
            "tags": ["devtools", "release-management"],
        }
        url = "https://forum.ansible.com/posts.json"
        request = Request(url)  # noqa: S310
        request.method = "POST"
        request.add_header("Api-Key", self.forum_api_key)
        request.add_header("Api-Username", self.forum_user)
        request.add_header("Content-Type", "application/json")
        data = json.dumps(payload).encode("utf-8")
        with urllib.request.urlopen(url=request, data=data) as url:  # noqa: S310
            _response = json.load(url)


def main() -> None:
    """Run the Post class."""
    parser = argparse.ArgumentParser(
        description="Post a release announcement to the Ansible forum.",
    )
    parser.add_argument("project", help="The project name.")
    parser.add_argument("release", help="The release version.")
    parser.add_argument("forum_api_key", help="The forum API key.")
    parser.add_argument("forum_user", help="The forum user.")
    args = parser.parse_args()
    post = Post(args.project, args.release, args.forum_api_key, args.forum_user)
    post.post()


if __name__ == "__main__":
    main()
