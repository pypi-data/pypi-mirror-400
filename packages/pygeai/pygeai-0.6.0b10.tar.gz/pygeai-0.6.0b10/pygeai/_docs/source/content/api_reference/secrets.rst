Secrets Management
==================

The Secrets Management module provides secure storage and access control for sensitive information such as API keys, passwords, and tokens. Secrets can be used by assistants, workflows, and other SDK components without exposing credentials in code.

This section covers:

* Creating and managing secrets
* Updating secret values
* Managing access permissions
* Listing and retrieving secrets

For each operation, you have three implementation options:

* `Command Line`_
* `Low-Level Service Layer`_
* `High-Level Service Layer`_

Overview
--------

Secrets in the SDK:

* **Secure Storage**: Encrypted at rest and in transit
* **Access Control**: Fine-grained permissions per secret
* **Centralized Management**: One place to manage all credentials
* **Integration**: Seamlessly usable across assistants and services
* **Versioning**: Update secrets without changing code

Create Secret
-------------

Creates a new secret with a name, value, and optional description.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai secrets create \
      --name "openai-api-key" \
      --secret-string "sk-..." \
      --description "OpenAI API key for production assistant"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.secrets.clients import SecretClient

    client = SecretClient()
    
    secret = client.create_secret(
        name="openai-api-key",
        secret_string="sk-...",
        description="OpenAI API key for production assistant"
    )
    
    print(f"Created secret: {secret['id']}")

**Parameters:**

* ``name``: (Required) Unique name for the secret
* ``secret_string``: (Required) The secret value to store
* ``description``: Optional description of the secret's purpose

**Returns:**
Dictionary containing the created secret with ID and metadata.

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

Currently uses the low-level client.


List Secrets
------------

Retrieves secrets with optional filtering and pagination.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai secrets list

.. code-block:: shell

    geai secrets list --name "openai" --count 20

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.secrets.clients import SecretClient

    client = SecretClient()
    
    # List all secrets (paginated)
    secrets = client.list_secrets(start=0, count=10)
    
    for secret in secrets.get('secrets', []):
        print(f"{secret['name']}: {secret['description']}")
    
    # Filter by name
    filtered = client.list_secrets(name="openai")

**Parameters:**

* ``name``: Optional filter by secret name (partial match)
* ``id``: Optional filter by secret ID
* ``start``: Starting index for pagination (default: 0)
* ``count``: Number of secrets to return (default: 10)

**Returns:**
Dictionary containing list of secrets with metadata (secret values are NOT included in list responses).


Get Secret
----------

Retrieves a specific secret by ID, including its value.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai secrets get --id "secret-uuid"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.secrets.clients import SecretClient

    client = SecretClient()
    
    secret = client.get_secret(secret_id="secret-uuid")
    
    print(f"Name: {secret['name']}")
    print(f"Value: {secret['secretString']}")
    print(f"Description: {secret['description']}")

**Parameters:**

* ``secret_id``: (Required) UUID of the secret to retrieve

**Returns:**
Dictionary containing the complete secret including its value.

**Security Note:** Only retrieve secret values when necessary. Use access controls to limit who can read secrets.


Update Secret
-------------

Updates an existing secret's value, name, or description.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai secrets update \
      --id "secret-uuid" \
      --name "openai-api-key-v2" \
      --secret-string "sk-new-key..." \
      --description "Updated OpenAI key"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.secrets.clients import SecretClient

    client = SecretClient()
    
    updated = client.update_secret(
        secret_id="secret-uuid",
        name="openai-api-key-v2",
        secret_string="sk-new-key...",
        description="Updated OpenAI key"
    )
    
    print(f"Updated secret: {updated['id']}")

**Parameters:**

* ``secret_id``: (Required) UUID of the secret to update
* ``name``: (Required) Updated name for the secret
* ``secret_string``: (Required) Updated secret value
* ``description``: Optional updated description

**Returns:**
Dictionary containing the updated secret metadata.


Manage Secret Access
--------------------

Set Secret Access Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configures who can access a secret and at what level.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai secrets set-access \
      --id "secret-uuid" \
      --access-level "write" \
      --principal-type "service"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.secrets.clients import SecretClient

    client = SecretClient()
    
    result = client.set_secret_accesses(
        secret_id="secret-uuid",
        access_list=[
            {
                "accessLevel": "write",
                "principalType": "service"
            },
            {
                "accessLevel": "read",
                "principalType": "user"
            }
        ]
    )
    
    print(f"Access configured for secret")

**Parameters:**

* ``secret_id``: (Required) UUID of the secret
* ``access_list``: (Required) List of access configurations, each containing:
  
  * ``accessLevel``: Access level (e.g., "read", "write")
  * ``principalType``: Type of principal (e.g., "service", "user")

**Returns:**
Dictionary confirming access configuration.


Get Secret Access Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieves current access permissions for a secret.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.secrets.clients import SecretClient

    client = SecretClient()
    
    accesses = client.get_secret_accesses(secret_id="secret-uuid")
    
    for access in accesses.get('accessList', []):
        print(f"Principal: {access['principalType']}, Level: {access['accessLevel']}")

**Parameters:**

* ``secret_id``: (Required) UUID of the secret

**Returns:**
Dictionary containing the list of access configurations.


Complete Usage Example
----------------------

.. code-block:: python

    from pygeai.core.secrets.clients import SecretClient

    client = SecretClient()

    # Create a secret for API key
    api_secret = client.create_secret(
        name="third-party-api-key",
        secret_string="pk_live_abc123xyz...",
        description="Production API key for payment processor"
    )
    secret_id = api_secret['id']
    print(f"Created secret with ID: {secret_id}")

    # Set access permissions
    client.set_secret_accesses(
        secret_id=secret_id,
        access_list=[
            {"accessLevel": "write", "principalType": "service"},
            {"accessLevel": "read", "principalType": "user"}
        ]
    )
    print("Access permissions configured")

    # List all secrets
    all_secrets = client.list_secrets(count=50)
    print(f"\nTotal secrets: {len(all_secrets.get('secrets', []))}")

    # Update secret value when key rotates
    client.update_secret(
        secret_id=secret_id,
        name="third-party-api-key",
        secret_string="pk_live_new_key_789...",
        description="Rotated API key - updated 2026-01-07"
    )
    print("\nSecret value updated")

    # Retrieve secret for use
    secret_data = client.get_secret(secret_id=secret_id)
    api_key = secret_data['secretString']
    # Use api_key in your application...


Integration with Assistants
----------------------------

Secrets can be referenced in assistant configurations to avoid hardcoding credentials:

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager
    from pygeai.core.secrets.clients import SecretClient

    # Store API key as secret
    secret_client = SecretClient()
    api_secret = secret_client.create_secret(
        name="assistant-llm-key",
        secret_string="sk-...",
        description="LLM API key for assistant"
    )

    # Reference secret in assistant configuration
    # (Implementation depends on assistant type and API support)
    assistant_manager = AssistantManager()
    # ... configure assistant to use secret by ID or name


Best Practices
--------------

Secret Naming
~~~~~~~~~~~~~

* Use descriptive, hierarchical names: ``service-environment-purpose``
* Examples:
  
  * ``openai-prod-assistant-key``
  * ``database-staging-password``
  * ``slack-webhook-notifications``

* Use lowercase with hyphens for consistency
* Avoid including the secret value or sensitive info in the name

Secret Rotation
~~~~~~~~~~~~~~~

* Regularly rotate sensitive credentials
* Update secrets using ``update_secret()`` rather than deleting and recreating
* Document rotation schedule in secret description
* Test after rotation to ensure services still work

Access Control
~~~~~~~~~~~~~~

* Apply principle of least privilege
* Use "read" access for services that only consume secrets
* Reserve "write" access for administrative operations
* Review access permissions regularly

Security
~~~~~~~~

* Never log or print secret values
* Don't commit secrets to version control
* Use secrets for all sensitive configuration
* Retrieve secret values only when needed (lazy loading)
* Clear secret values from memory after use

Organization
~~~~~~~~~~~~

* Group related secrets with common prefixes
* Use descriptions to document purpose, owner, and rotation schedule
* Maintain an inventory of secrets and their usage
* Clean up unused secrets promptly


Error Handling
--------------

.. code-block:: python

    from pygeai.core.secrets.clients import SecretClient
    from pygeai.core.common.exceptions import APIError

    client = SecretClient()

    # Handle missing secret
    try:
        secret = client.get_secret(secret_id="nonexistent-id")
    except APIError as e:
        print(f"Secret not found: {e}")

    # Handle validation errors
    try:
        client.create_secret(
            name="",  # Invalid: empty name
            secret_string="value"
        )
    except ValueError as e:
        print(f"Validation error: {e}")

    # Handle duplicate names
    try:
        client.create_secret(
            name="existing-secret",
            secret_string="value"
        )
    except APIError as e:
        print(f"Secret already exists: {e}")


Common Issues
~~~~~~~~~~~~~

**Empty Secret Name or Value**

.. code-block:: python

    # ❌ Wrong
    client.create_secret(name="", secret_string="value")
    
    # ✅ Correct
    client.create_secret(name="my-secret", secret_string="value")

**Missing Access Level or Principal Type**

.. code-block:: python

    # ❌ Wrong
    client.set_secret_accesses(
        secret_id="id",
        access_list=[{"accessLevel": "read"}]  # Missing principalType
    )
    
    # ✅ Correct
    client.set_secret_accesses(
        secret_id="id",
        access_list=[
            {"accessLevel": "read", "principalType": "service"}
        ]
    )

**Retrieving Secret Value in List**

.. code-block:: python

    # ❌ Wrong - list_secrets() doesn't include secret values
    secrets = client.list_secrets()
    value = secrets[0]['secretString']  # This field doesn't exist
    
    # ✅ Correct - use get_secret() to retrieve value
    secrets = client.list_secrets()
    secret_id = secrets['secrets'][0]['id']
    secret_data = client.get_secret(secret_id=secret_id)
    value = secret_data['secretString']


Notes
-----

* Secret values are never returned in list operations (only in get_secret)
* Secret IDs are UUIDs generated by the system
* Deleting a secret is permanent and cannot be undone
* Access levels and principal types depend on your organization's configuration
* Pagination helps manage large numbers of secrets efficiently
