# Ansible developer tools personas

Personas represent various humans who are on different automation journeys with Ansible.
This set of personas puts users of Ansible developer tools in context to better identify their technical content needs at each stage of their respective journeys.

The practical goal of defining these personas is to improve the completeness and usefulness of Ansible developer tools documentation.
As a result documentation puts help when and where users need it, leading to higher levels of adoption and increased user success.

# Novice

I am an engineer or programmer who has little or no experience with Ansible automation.
I have a single repeatable task that I perform as part of my job and I want to automate that in a consistent way.

- **Needs:** Getting started content. Basic concepts. Guidance on best practices and conventions.
- **Attitude:** Wants to understand things quickly and can find small obstacles frustrating.
- **Knowledge:** Strong knowledge of fundamentals of computing. Uses an IDE as part of the daily workflow.

# IT automation engineer

I create automation content, composed of multiple tasks or playbooks, that runs against single platforms.
I want to reuse automation content where possible and share automation content with others.
I work independently or with a small team and have an innovative mindset with strong problem-solving ability.

- **Needs:** Task-oriented content focused on building and testing automation content. Conceptual details related to organizing and structuring projects. Extensive reference content that explains "if you do x, then y is the expected behaviour".
- **Attitude:** Wants to understand how things work and what the available options are.
- **Knowledge:** Strong knowledge of CI/CD platforms and tools. Expert with scripting languages.

# Process automation engineer

I create end-to-end automation solutions across multiple services or applications.
I also manage things like inventories and credentials and work with cross-functional teams to oversee testing, delivery, and validation of solutions.
In my role I use CI/CD pipelines to provision cloud resources and integrate solutions on a continual basis. I create separate stage and production environments.

- **Needs:** Opinionated task-oriented content at the solution level.
- **Attitude:** Wants to know the "one right way" to perform a task in a repeatable, predictable way. Cares about visibility, governance, KPIs, and SLA requirements (99.999 24/7).
- **Knowledge:** Deep understanding of Linux and open-source technologies. Expert with configuration management and orchestration tooling.

# Operations engineer

I manage and maintain Ansible automation infrastructure using AWX or Controller.
In my role I do not create automation content directly but am responsible for provisioning IT services that are stable and comply with the standards and practices that protect my company's IT operations and business reputation.

- **Needs:** Quick and immediate actions to take when resolving specific error conditions.
- **Attitude:** Wants to see and diagnose issues as quickly as possible. Needs alerts when malfunctions occur, a flashing red light on the dashboard.
- **Knowledge:** Deep understanding of Linux and open-source technologies. Proficient with monitoring and logging tools.

# Automation developer

I write automation content that users of a partner or vendor platform can consume, with a focus on Ansible plugins and modules in Python or other programming languages.
I might work with the community to maintain one or more collections as part of the Ansible package.
In some cases, I create and distribute collections through other channels or mechanisms.
In my role I might also be interested in community tooling such as Antsibull or other projects in the ecosystem.

- **Needs:** Understand programmatic options and their expected behaviour. Guidance on lifecycles and maintenance best practices.
- **Attitude:** Technically curious and prefers verbosity. Often busy with another more primary role.
- **Knowledge:** Expert level programming ability.
