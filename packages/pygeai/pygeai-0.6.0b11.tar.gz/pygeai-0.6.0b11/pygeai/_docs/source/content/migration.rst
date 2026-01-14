Migration Guide
===============

Overview
--------

The GEAI SDK provides powerful migration capabilities that allow you to clone and migrate projects and their resources between different GEAI instances or within the same instance. This feature is essential for:

- **Environment promotion**: Moving projects from development to staging to production
- **Backup and disaster recovery**: Creating copies of projects for safety
- **Multi-tenant deployments**: Replicating project setups across different organizations
- **Testing and experimentation**: Creating isolated copies for testing changes

The migration feature supports migrating the following resource types:

- **Agents**: AI agents with their configurations and prompts
- **Tools**: Custom tools and integrations
- **Agentic Processes**: Multi-step agentic workflows
- **Tasks**: Individual task definitions
- **Usage Limits**: Resource usage constraints and quotas
- **RAG Assistants**: Retrieval-Augmented Generation assistants
- **Files**: Project files and attachments

Key Features
------------

**Selective Migration**
  Migrate specific resources by ID or migrate all resources of a given type using the ``all`` keyword.

**Bulk Migration**
  Use the ``--all`` flag to migrate every available resource type in a single command.

**Cross-Instance Migration**
  Migrate projects between different GEAI instances with different API credentials.

**Same-Instance Cloning**
  Clone projects within the same instance for testing or backup purposes.

**Automatic Resource Discovery**
  When using ``all``, the migration tool automatically discovers and migrates all existing resources.

**Flexible Destination**
  Migrate to a new project or to an existing project in the same or different instance.

Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

Before migrating, you need:

1. **Source credentials**: API key and instance URL for the source project
2. **Destination credentials**: API key and instance URL (can be the same as source)
3. **Project identifiers**: Source project ID
4. **Admin email**: Required when creating a new destination project

API Token Scopes
~~~~~~~~~~~~~~~~~

Different migration operations require different API token scopes:

**Organization Scope Tokens**
  Required for operations that create or manage projects and organization-level resources:
  
  - **Project Creation**: Creating new projects requires organization scope API keys (``--from-org-key`` and ``--to-org-key``)
  - **Usage Limit Migration**: Managing usage limits requires organization scope API keys
  
  For more information, see the `Organization API Documentation <https://docs.globant.ai/en/wiki?22,Organization+API>`_ and `Usage Limits API Documentation <https://docs.globant.ai/en/wiki?802,Usage+Limits+API>`_.

**Project Scope Tokens**
  Required for operations within a project:
  
  - **Agent Migration**: Migrating agents within projects
  - **Tool Migration**: Migrating tools within projects
  - **Agentic Process Migration**: Migrating agentic processes
  - **Task Migration**: Migrating tasks
  - **RAG Assistant Migration**: Migrating RAG assistants
  - **File Migration**: Migrating files within projects

Migration Scenarios and Required Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The required API keys depend on whether you're creating a new project or migrating to an existing one:

**Scenario 1: Creating a New Project**
  When using ``--to-project-name`` and ``--admin-email``:
  
  - ``--from-api-key``: **Project scope** token for reading source resources
  - ``--from-org-key``: **Organization scope** token (REQUIRED for project creation)
  - ``--to-org-key``: **Organization scope** token for destination instance (REQUIRED, or use ``--from-org-key`` for same instance)
  - ``--to-api-key``: OPTIONAL - If not provided, a project scope API key will be automatically created for the new project
  
  The migration tool will:
  
  1. Create the new project using organization scope keys
  2. Automatically generate a project scope API key for the new project
  3. Use the generated key to migrate all resources

**Scenario 2: Migrating to an Existing Project**
  When using ``--to-project-id``:
  
  - ``--from-api-key``: **Project scope** token for reading source resources (REQUIRED)
  - ``--to-api-key``: **Project scope** token for writing to destination project (REQUIRED)
  - Organization scope keys are NOT needed for resource migration
  
.. warning::
   When migrating to an existing project (using ``--to-project-id``), you MUST provide ``--to-api-key``. This is a project scope token that has write access to the destination project.

Basic Usage
-----------

Migrate Everything
~~~~~~~~~~~~~~~~~~

The simplest and most common use case is to migrate an entire project with all its resources:

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p" \\
        --from-instance "https://api.source.example.ai" \\
        --to-project-name "Cloned Project" \\
        --admin-email "admin@example.com" \\
        --all

This command will:

1. Create a new project named "Cloned Project"
2. Discover all resources in the source project
3. Migrate all agents, tools, processes, tasks, usage limits, RAG assistants, and files
4. Display progress and results

Migrate to Different Instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To migrate between different GEAI instances, provide the destination instance details:

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.dev.example.ai" \\
        --to-api-key "destination_api_key_456" \\
        --to-project-name "Production Project" \\
        --to-instance "https://api.prod.example.ai" \\
        --to-organization-id "prod-org-id" \\
        --admin-email "prod-admin@example.com" \\
        --all

Selective Migration
-------------------

Migrate Specific Resource Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of migrating everything, you can selectively migrate specific resource types:

**Migrate all agents only:**

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-project-name "Agents Only" \\
        --admin-email "admin@example.com" \\
        --agents all

**Migrate all tools only:**

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-project-name "Tools Only" \\
        --admin-email "admin@example.com" \\
        --tools all

**Migrate all RAG assistants only:**

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-project-name "RAG Assistants Only" \\
        --admin-email "admin@example.com" \\
        --rag-assistants all

Migrate Specific Resources by ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For fine-grained control, specify comma-separated resource IDs:

**Migrate specific agents:**

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-project-name "Selected Agents" \\
        --admin-email "admin@example.com" \\
        --agents "agent-id-1,agent-id-2,agent-id-3"

**Migrate specific tools:**

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-project-name "Selected Tools" \\
        --admin-email "admin@example.com" \\
        --tools "tool-id-1,tool-id-2"

Mixed Migration Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Combine different migration strategies for maximum flexibility:

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-project-name "Mixed Migration" \\
        --admin-email "admin@example.com" \\
        --agents all \\
        --tools "tool-id-1,tool-id-2" \\
        --rag-assistants all \\
        --files all

This command migrates:

- **ALL** agents (auto-discovered)
- **SPECIFIC** tools (by ID)
- **ALL** RAG assistants (auto-discovered)
- **ALL** files (auto-discovered)

Advanced Usage
--------------

Migrate with Organization Context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When migrating between organizations, specify organization IDs:

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-organization-id "source-org-id" \\
        --from-instance "https://api.example.ai" \\
        --to-api-key "destination_api_key_456" \\
        --to-project-name "Cross-Org Project" \\
        --to-organization-id "destination-org-id" \\
        --to-instance "https://api.example.ai" \\
        --admin-email "admin@example.com" \\
        --all

Migrate All AI Lab Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To migrate all AI Lab-related resources (agents, tools, processes, tasks):

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_api_key_123" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-project-name "AI Lab Resources" \\
        --admin-email "admin@example.com" \\
        --agents all \\
        --tools all \\
        --agentic-processes all \\
        --tasks all

CLI Reference
-------------

Command: ``geai migrate clone-project``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Description:** Clone a project with selective or complete resource migration.

**Required Arguments:**

``--from-api-key <key>``
  Project scope API key for the source GEAI instance (for migrating resources)

``--from-project-id <id>``
  ID of the source project to migrate from

``--from-instance <url>``
  URL of the source GEAI instance

**Optional Arguments:**

``--from-org-key <key>``
  Organization scope API key for the source instance (REQUIRED when creating projects or migrating usage limits)

``--to-api-key <key>``
  Project scope API key for the destination instance. **REQUIRED** when using ``--to-project-id`` (existing project). OPTIONAL when creating a new project (auto-generated if not provided)

``--to-org-key <key>``
  Organization scope API key for the destination instance (REQUIRED when creating projects or migrating usage limits)

``--to-project-id <id>``
  Destination project ID (use this to migrate to an existing project). **REQUIRED**: ``--to-api-key`` must also be provided. **MUTUALLY EXCLUSIVE** with ``--to-project-name`` and ``--admin-email``

``--to-project-name <name>``
  Name for the new destination project (when specified with --admin-email, creates a new project). **MUTUALLY EXCLUSIVE** with ``--to-project-id``

``--admin-email <email>``
  Admin email for the new project (required when creating a new project with --to-project-name)

``--to-instance <url>``
  URL of the destination instance (defaults to source instance if omitted)

``--from-organization-id <id>``
  Organization ID in the source instance (required for usage limits and file migration)

``--to-organization-id <id>``
  Organization ID in the destination instance (required for usage limits and file migration)

**Migration Flags:**

``--all``
  Migrate all available resource types (agents, tools, processes, tasks, usage limits, RAG assistants, files)

``--agents <all|id1,id2,...>``
  Migrate all agents or specific agents by ID (comma-separated)

``--tools <all|id1,id2,...>``
  Migrate all tools or specific tools by ID (comma-separated)

``--agentic-processes <all|id1,id2,...>``
  Migrate all agentic processes or specific processes by ID (comma-separated)

``--tasks <all|id1,id2,...>``
  Migrate all tasks or specific tasks by ID (comma-separated)

``--usage-limits <all|id1,id2,...>``
  Migrate all usage limits or specific usage limits by ID (comma-separated)

``--rag-assistants <all|id1,id2,...>``
  Migrate all RAG assistants or specific assistants by ID (comma-separated)

``--files <all|id1,id2,...>``
  Migrate all files or specific files by ID (comma-separated)

``--stop-on-error <0|1>`` or ``--soe <0|1>``
  Control migration behavior on errors. Set to ``1`` (default) to stop migration on first error, or ``0`` to continue migrating remaining resources even if some fail

Migration Behavior
------------------

Resource Discovery
~~~~~~~~~~~~~~~~~~

When you use ``all`` for any resource type, the migration tool:

1. Connects to the source instance
2. Lists all available resources of that type
3. Filters resources with valid IDs/names
4. Creates migration strategies for each discovered resource
5. Displays the count of discovered resources

For example:

.. code-block:: shell

    geai migrate clone-project ... --agents all

Will output something like:

.. code-block:: text

    Discovered 15 agents
    Migrating agents...
    [Progress indicators]

Error Handling
~~~~~~~~~~~~~~

The migration process includes robust error handling:

- Invalid API keys or instances result in clear error messages
- Missing required parameters are detected before migration starts
- Individual resource migration failures are logged but don't stop the entire process by default (unless ``--stop-on-error 1`` is set)
- Final migration result includes success/failure status for each resource
- Use ``--stop-on-error 0`` to continue migrating all resources even if some fail, or ``--stop-on-error 1`` (default) to halt on first error

Best Practices
--------------

1. **Test First**: Always test migrations in a development environment before production
2. **Use --all for Complete Clones**: When creating backups or full clones, use ``--all``
3. **Verify Credentials**: Double-check API keys and instance URLs before running migrations
4. **Monitor Progress**: Watch the console output for discovery counts and migration status
5. **Check Results**: Review the migration result summary after completion
6. **Incremental Migration**: For large projects, consider migrating resource types incrementally
7. **Document Migrations**: Keep track of what was migrated and when

Common Use Cases
----------------

Development to Production Promotion (with new project creation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "dev_project_api_key" \\
        --from-org-key "dev_org_api_key" \\
        --from-project-id "dev-project-id" \\
        --from-instance "https://api.dev.example.ai" \\
        --to-api-key "prod_project_api_key" \\
        --to-org-key "prod_org_api_key" \\
        --to-project-name "Production Release v1.0" \\
        --to-instance "https://api.prod.example.ai" \\
        --admin-email "prod-admin@example.com" \\
        --all

Project Backup (with new project creation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "project_api_key" \\
        --from-org-key "org_api_key" \\
        --from-project-id "main-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-org-key "org_api_key" \\
        --to-project-name "Main Project Backup $(date +%Y-%m-%d)" \\
        --admin-email "admin@example.com" \\
        --all

Migrate Resources to Existing Project (no org keys needed)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When migrating to an existing project, you must provide both ``--to-project-id`` and ``--to-api-key``:

.. code-block:: shell

    geai migrate clone-project \\
        --from-api-key "source_project_api_key" \\
        --from-project-id "source-project-id" \\
        --from-instance "https://api.example.ai" \\
        --to-project-id "existing-project-id" \\
        --to-api-key "target_project_api_key" \\
        --agents all \\
        --tools all

This example migrates all agents and tools to an existing project without requiring organization scope API keys.

Troubleshooting
---------------

Migration Fails with Authentication Error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``Error retrieving project_id from GEAI: Authentication failed``

**Solution**: Verify your API keys are correct and have necessary permissions:

- When creating a new project (``--to-project-name`` + ``--admin-email``): You MUST provide **organization scope** API keys via ``--from-org-key`` and ``--to-org-key``
- When migrating usage limits (``--usage-limits``): You MUST provide **organization scope** API keys via ``--from-org-key`` and ``--to-org-key``
- For other resource migrations: Use **project scope** API keys via ``--from-api-key`` and ``--to-api-key``

Missing Organization Scope API Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``Source organization scope API key (--from-org-key) is required for project creation``

**Solution**: When creating a new project or migrating usage limits, you must explicitly provide organization scope API keys using ``--from-org-key`` and ``--to-org-key`` parameters. Project scope API keys cannot be used for these operations

Missing Destination Project API Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``Destination project API key (--to-api-key) is required when migrating to an existing project (--to-project-id)``

**Solution**: When migrating to an existing project using ``--to-project-id``, you MUST provide ``--to-api-key`` with a project scope API key that has write access to the destination project. This is required because the migration tool needs to create resources in the existing project.

**Note**: When creating a NEW project (using ``--to-project-name`` and ``--admin-email``), ``--to-api-key`` is optional and will be automatically generated if not provided.

Migration Discovers No Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``Discovered 0 agents`` when you know resources exist

**Solution**: Check that the ``--from-project-id`` is correct and the API key has read access

Partial Migration Success
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Some resources migrate successfully, others fail

**Solution**: Check the error log for specific resource failures and retry individual resources if needed

Limitations
-----------

- API rate limits may affect large migrations
- Some resource dependencies may require specific migration order
- Cross-instance migrations require network connectivity between instances
- Certain resource types may have instance-specific configurations

See Also
--------

- :doc:`cli` - General CLI usage
- :doc:`ai_lab` - AI Lab concepts and resources
- :doc:`quickstart` - Getting started with GEAI SDK
