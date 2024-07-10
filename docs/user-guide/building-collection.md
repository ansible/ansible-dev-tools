# Building Ansible Collection using Unified Tooling

This guide illustrates a comprehensive Ansible development workflow that showcases the integration of various tools within the Ansible ecosystem to create an Ansible collection. The tools featured in this workflow include:

- [ansible-creator](https://github.com/ansible/ansible-creator)
- [ansible-dev-environment (ansible-dev-environment)](https://github.com/ansible/ansible-dev-environment)
- [ansible-lint](https://github.com/ansible/ansible-lint)
- [ansible-navigator](https://github.com/ansible/ansible-navigator)
- [VS Code Ansible extension](https://github.com/ansible/vscode-ansible)

## Scaffolding a collection using ansible-creator

- Open VS Code and click the Ansible icon in the activity bar to access Ansible Creator section. Click on "Get Started" under that section to open the menu page of Ansible Creator in VS Code.

- Check system requirements and install ansible-creator if needed. Ensure all requirements in the `system requirements` box have green ticks.

- Click "Initialize a collection" to open the "Init" interface. Fill the form with the collection name, initialization path, verbosity, and logging options. Click "Create" to scaffold the collection in the desired location. You have the open to review the logs or open the log file in VS Code editor for details.

- Click on `Open collection` button to add the collection folder to the workspace.

<video width="100%" controls autoplay loop>
<source src="../../media/create-collection.mp4" type="video/mp4">
</video>

NOTE: For a more detailed explanation about using Ansible Creator in the VS Code Ansible Extension, refer to [doc: ansible-creator].

## Installing the collection using ansible-dev-environment

- With the initial collection structure in place, use 'ansible-dev-environment' to install the newly created collection in editable mode, similar to Python modules.

- Navigate to the collection directory and run:

```console
$ ade install -e .
```

- This installation method adds the collection to the system paths so that Ansible knows about it. Additionally, it enhances the development process by allowing on-the-go changes to the module code.

- You can check if the collection is installed or not by using ansible-galaxy command. In the terminal, running the following command should show the name of the newly created collection:

```console
$ ansible-galaxy collection list
```

## Add python code to bring the collection to life

- Navigate to the collection directory and navigate to plugins/modules/. Add create a [module-name].py file and documentation, examples and logic to the module.

- Due to its installation method using pip4a, you can change module code dynamically and observe the effects during playbook execution.

NOTE: for details regarding the module development, refer to the [ansible module development docs](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html).

## Using ansible-lint to check module syntax in the playbook

- Leverage vscode-ansible extension and ansible-lint to gain insights into the collection without running the playbook

- Create a simple playbook under the 'playbooks' directory.

- Once you have completed writing the playbook that uses the newly created collection module, saving the file will automatically run ansible-lint on the playbook.

- With its integration in the extension, ansible-lint can detect mistakes, such as incorrect option values and missing required options, along with other rules for ansible best practices by providing feedback in the editor (red and yellow squiggly lines) and inside the `Problems` tab in the vscode.

<video width="100%" controls autoplay loop>
<source src="../../media/ansible-lint.mp4" type="video/mp4">
</video>

## Using ansible-navigator to tun the playbook with the collection module

- The Ansible extension in VS Code has the ability to detect the playbook files and provide several
  Ansible related options for it. One such option is to run the playbook without having to leave the editor.

- Right-click on the opened playbook in the editor and choose `Run Ansible Playbook via`. This provides options to run the playbook via ansible-navigator or ansible-playbook.

- Select `Run playbook via ansible-navigator run` to execute the playbook in the terminal within VS Code.

<video width="100%" controls autoplay loop>
<source src="../../media/ansible-navigator-run.mp4" type="video/mp4">
</video>

## Adapting to changes in the module code

- This is a good time to experiment with the power of `installing a collection in editable mode`. Make changes in the module code by adding new functionality and/or modifying the existing functionalities.

- Repeat the previous two steps to observe how the extension and ansible-lint seamlessly adapt to the changes.

- The Ansible extension along with ansible-lint continues to provide linting functionalities for the updated module code and running the playbook using ansible-navigator incorporates the new module code seamlessly.

This unified development suite, incorporating ansible-creator, ansible-dev-environment, ansible-lint, ansible-navigator, and vscode-ansible extension, enables content developers with an enhanced and efficient method for their Ansible development workflow.

The integration of these tools streamlines the development process, offering a cohesive experience for building Ansible Collections.
