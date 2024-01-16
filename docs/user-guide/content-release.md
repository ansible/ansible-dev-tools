# Using the Release workflow

The following GitHub Actions are to be placed added under `.github/workflows` directory as `{filename}.yaml`
This GitHub action releases the collection in Ansible Automation Hub and Ansible Galaxy, it is dependent on the environment `release` which must contain the following secrets.

`AH_TOKEN`: The Automation Hub token required for to interact with Ansible Automation Hub.
`ANSIBLE_GALAXY_API_KEY`: A Galaxy token required to interact with Ansible Galaxy.

Note - ansible-content-actions/release.yaml uses release_ah.yaml and release_galaxy.yaml internally.

Filename: `release.yaml`

```
---
name: "Release collection"
on:
  release:
    types: [published]

jobs:
  release:
    uses: ansible/ansible-content-actions/.github/workflows/release.yaml@main
    with:
      environment: release
    secrets:
      ah_token: ${{ secrets.AH_TOKEN }}
      ansible_galaxy_api_key: ${{ secrets.ANSIBLE_GALAXY_API_KEY }}
```

The workflow run results in -

![Alt text](./images/release.png?raw=true "Release collection")

The release works in two parts, Automation hub release and then Ansible Galaxy release. If the Automation hub release fails, the Galaxy job is skipped.

Example showing how only Automation hub release can be made, only `ah_token` would be required in those cases.

### Release on AH only, workflow

Filename: `release.yaml`

```
---
name: "Release collection on Automation Hub"
on:
  release:
    types: [published]

jobs:
  release_automation_hub:
    uses: ansible/ansible-content-actions/.github/workflows/release_ah.yaml@main
    with:
      environment: release
    secrets:
      ah_token: ${{ secrets.AH_TOKEN }}
```

### Release on Galaxy only, workflow

Filename: `release.yaml`

```
---
name: "Release collection on Ansible Galaxy"
on:
  release:
    types: [published]

jobs:
  release_automation_hub:
    uses: ansible/ansible-content-actions/.github/workflows/release_galaxy.yaml@main
    with:
      environment: release
    secrets:
      ah_token: ${{ secrets.ANSIBLE_GALAXY_API_KEY }}
```

## Detailed release process

### Things to make sure of before release:

#### Environments:

The repo that is being released must have the following environments created:

- **Name: release**

  - `AH_TOKEN`
  - `ANSIBLE_GALAXY_API_KEY`

- **Name: push**

  - `BOT_PAT`

- `refresh_ah_token`: Make sure this workflow in netcommon has run successfully in the previous run. If not, it must be triggered to re-run and ensure it is successfully executed.

#### Prepare the repo for release (draft_release workflow only uses BOT_PAT, i.e., Ansibuddy):

This step is to be substituted by a manual run of the push workflow, which is currently not recommended as the behavior is unstable. In terms of generating a changelog.

1. Start preparing the repo for release: Run `antsibull-changelog` on the repo locally, make a PR, and get it merged.
2. Now we are set to release.

Make sure `galaxy.yml` is in sync with the release version. The version pushed in Galaxy and AH is referenced from `version:` in `galaxy.yml`.

#### Release process through GitHub:

1. Go to the releases page in GitHub UI and create a new release.
2. Create a new tag and name it in this format - `v[version_num]` - e.g., `v5.2.1`.
   - Note: The `v` prefix exists in the GH tag and is redacted in AH and Galaxy releases.
3. Name the title the same as the tag.
4. Put in the changelog - which can be found in `CHANGELOG.rst` (RAW).
5. Push the release button, and it will release the collection.
6. Look out for the release action in the Actions tab. The AH release happens first, followed by the Galaxy release. If the AH release fails, the Galaxy release fails too.
