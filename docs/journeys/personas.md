# Ansible developer tools personas

Personas represent various humans who are on different automation journeys with Ansible.
This set of personas puts users of Ansible developer tools in context to better identify their technical content needs at each stage of their respective journeys.

The practical goal of defining these personas is to improve the completeness and usefulness of Ansible developer tools documentation.
As a result documentation puts help when and where users need it, leading to higher levels of adoption and increased user success.

# Novice

I am an engineer or programmer who has little or no experience with Ansible automation.
I have a single repeatable task that I perform as part of my job and I want to automate that in a consistent way.

- **Needs:** Integrated tooling, getting set up efficiently. Guidance on best practices and conventions.
- **Attitude:** Wants to understand basic concepts quickly and can find small obstacles frustrating.
- **Knowledge:** Strong knowledge of fundamentals of computing. Uses an IDE as part of the daily workflow.

# Software automation engineer

I create automation content, composed of multiple tasks or playbooks, that runs against single platforms.
I want to reuse automation content where possible and share automation content with others.

- **Needs:** Organize and structure for playbooks and roles. Ability to test automation content.
- **Attitude:** Works independently or with a small team. Innovative mindset with strong problem-solving ability.
- **Knowledge:** Proficient with CI/CD platforms and tools. Excellent scripting skills.

# Process automation engineer

I create end-to-end automation solutions across multiple services or applications.
I also manage things like inventories and credentials.

- **Needs:** Ensure automation solutions meet standards
- **Attitude:** Works with cross-functional teams to oversee testing, delivery, and validation of solutions.
- **Knowledge:** Uses CI/CD pipelines to provision cloud resources and integrate solutions from the development team on a continual basis. Creates separate stage and production environments.

# Operations engineer

I manage and maintain Ansible automation infrastructure using AWX or Controller.
In my role I do not create automation content directly but am responsible for provisioning IT services that are stable and comply with the standards and practices that protect my company's IT operations and business reputation.

- **Needs:** Opinionated content with best practices. Quick and immediate actions to take when resolving specific error conditions.
- **Attitude:** Wants to know the "one right way" to perform a task in a repeatable, predictable way. Cares about visibility, governance, KPIs, and SLA requirements (99.999 24/7).
- **Knowledge:** Deep understanding of Linux and open-source technologies. Proficient with monitoring and logging tools.

# Developer

I write automation content that users of a partner or vendor platform can consume.

- **Needs:** Understand programmatic options and their expected behaviour.
- **Attitude:** Technically curious and prefers verbosity.
- **Knowledge:** Expert level programming ability.
