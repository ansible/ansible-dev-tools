# Ansible developer tools journeys

This document extends Ansible developer tools personas by identifying and describing their automation journeys.

[Ansible developer tools personas](personas.md)

## Intro

Each persona has specific milestones in their automation journey.
And each milestone has specific major actions that the persona achieves.
The first milestone of each journey starts with human motivation.

```yaml
Milestone: Aware
  Major action
  Major action
  ...
Milestone: Evaluate
  Major action
  Major action
  ...
Milestone: Adopt
  Major action
  Major action
  ...
Milestone: Scale
  Major action
  Major action
  ...
```

## Novice

The novice journey can be the basis for the "Getting started with Ansible Developer Tools" documentation.

```yaml
Milestone: Learn about Ansible Developer Tools
  Install VScode
  Install Ansible VScode extension
  Create a playbook from an example
  - Use code completion in VScode
  - Get lint feedback and resolve any errors
  - Run the playbook locally with ansible-playbook

Milestone: Write first playbook
  Scaffold a playbook in VScode
  Change lint profile to decrease verbosity
  Connect to lightspeed
  Add local credentials
  Create a basic, unstructured inventory
  - Become aware of groups

Milestone: Run the playbook against non-production systems
  Start using navigator
  - Run with TUI
  - Run with execution environment
  Run with AWX or Controller

Milestone: Add the playbook to source control
  Become aware of Publish to GitHub functionality in VSCode
  Learn about best practices for automation projects such as consistent structure and meaningful commit messages
  Understand the benefits of an ephemeral approach to development environments
```
