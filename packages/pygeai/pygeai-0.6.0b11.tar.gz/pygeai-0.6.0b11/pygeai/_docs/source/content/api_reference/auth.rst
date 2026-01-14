Authentication & Token Management
==================================

The GEAI SDK provides functionality to manage authentication and API tokens for Globant Enterprise AI. This includes OAuth2 authentication, user profile retrieval, and project API token management through the command line interface and the low-level service layer (AuthClient).

OAuth2 Access Token
~~~~~~~~~~~~~~~~~~~

Retrieves an OAuth2 access token for authentication with Globant Enterprise AI. This token is required for accessing user profile information and other authenticated endpoints.

Command Line
^^^^^^^^^^^^

The `geai auth get-access-token` command retrieves an OAuth2 access token using client credentials and user authentication.

.. code-block:: shell

    geai auth get-access-token \
      --client-id "your-client-id" \
      --username "user@example.com" \
      --password "your-password" \
      --scope "gam_user_data gam_user_roles"

Using short form aliases:

.. code-block:: shell

    geai auth gat \
      --cid "your-client-id" \
      -u "user@example.com" \
      -p "your-password" \
      -s "gam_user_data gam_user_roles"

Low Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

The `AuthClient` class provides a low-level interface to obtain OAuth2 access tokens.

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.get_oauth2_access_token(
        client_id="your-client-id",
        username="user@example.com",
        password="your-password",
        scope="gam_user_data gam_user_roles"
    )
    print(response)

User Profile Information
~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieves user profile information using an OAuth2 access token obtained from the previous endpoint.

Command Line
^^^^^^^^^^^^

The `geai auth get-user-info` command retrieves the current user's profile information.

.. code-block:: shell

    geai auth get-user-info \
      --access-token "your-access-token"

Using short form aliases:

.. code-block:: shell

    geai auth gui \
      --token "your-access-token"

Low Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

The `AuthClient` class provides a low-level interface to retrieve user profile information.

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.get_user_profile_information(
        access_token="your-access-token"
    )
    print(response)

Create Project API Token
~~~~~~~~~~~~~~~~~~~~~~~~~

Creates a new API token for a specific project. This operation requires organization-level or GAM authentication.

Command Line
^^^^^^^^^^^^

The `geai auth create-project-api-token` command creates a new API token for a project.

.. code-block:: shell

    geai auth create-project-api-token \
      --project-id "2ca6883f-6778-40bb-bcc1-85451fb11107" \
      --name "MyAPIToken" \
      --description "API token for production environment"

Creating a token without description (minimal):

.. code-block:: shell

    geai auth create-api-token \
      --pid "2ca6883f-6778-40bb-bcc1-85451fb11107" \
      --name "TestToken"

Using the shortest alias:

.. code-block:: shell

    geai auth cat \
      --pid "2ca6883f-6778-40bb-bcc1-85451fb11107" \
      -n "TestToken" \
      -d "Optional description"

Low Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

The `AuthClient` class provides a low-level interface to create project API tokens.

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.create_project_api_token(
        project_id="2ca6883f-6778-40bb-bcc1-85451fb11107",
        name="MyAPIToken",
        description="API token for production environment"
    )
    print(response)

Without description (optional parameter):

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.create_project_api_token(
        project_id="2ca6883f-6778-40bb-bcc1-85451fb11107",
        name="MyAPIToken"
    )
    print(response)

Get Project API Token
~~~~~~~~~~~~~~~~~~~~~~

Retrieves detailed information about a specific project API token.

Command Line
^^^^^^^^^^^^

The `geai auth get-project-api-token` command retrieves details of a specific API token.

.. code-block:: shell

    geai auth get-project-api-token \
      --api-token-id "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY"

Using short form aliases:

.. code-block:: shell

    geai auth get-api-token \
      --tid "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY"

Using the shortest alias:

.. code-block:: shell

    geai auth gat \
      --tid "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY"

Low Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

The `AuthClient` class provides a low-level interface to retrieve project API token details.

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.get_project_api_token(
        api_token_id="default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY"
    )
    print(response)

Update Project API Token
~~~~~~~~~~~~~~~~~~~~~~~~~

Updates an existing API token's description and/or status. Status can be set to 'active' or 'blocked'.

Command Line
^^^^^^^^^^^^

The `geai auth update-project-api-token` command updates an existing API token.

Update description only:

.. code-block:: shell

    geai auth update-project-api-token \
      --api-token-id "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY" \
      --description "Updated description for API token"

Update status to blocked:

.. code-block:: shell

    geai auth update-api-token \
      --tid "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY" \
      --status "blocked"

Update status to active:

.. code-block:: shell

    geai auth uat \
      --tid "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY" \
      --status "active"

Update both description and status:

.. code-block:: shell

    geai auth update-api-token \
      --api-token-id "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY" \
      --description "Production API token" \
      --status "active"

Low Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

The `AuthClient` class provides a low-level interface to update project API tokens.

Update description:

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.update_project_api_token(
        api_token_id="default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY",
        description="Updated description for API token"
    )
    print(response)

Update status:

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.update_project_api_token(
        api_token_id="default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY",
        status="blocked"
    )
    print(response)

Update both description and status:

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.update_project_api_token(
        api_token_id="default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY",
        description="Production API token",
        status="active"
    )
    print(response)

Delete Project API Token
~~~~~~~~~~~~~~~~~~~~~~~~~

Revokes an API token by setting its status to "revoked". Deleted tokens cannot be updated or reactivated.

Command Line
^^^^^^^^^^^^

The `geai auth delete-project-api-token` command deletes/revokes an API token.

.. code-block:: shell

    geai auth delete-project-api-token \
      --api-token-id "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY"

Using short form aliases:

.. code-block:: shell

    geai auth delete-api-token \
      --tid "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY"

Using the shortest alias:

.. code-block:: shell

    geai auth dat \
      --tid "default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY"

Low Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

The `AuthClient` class provides a low-level interface to delete project API tokens.

.. code-block:: python

    from pygeai.auth.clients import AuthClient

    client = AuthClient()

    response = client.delete_project_api_token(
        api_token_id="default_rnLl2eCuOuXJ_e8y8pXLMCnp1p4WcNu0I_-9mtD-AzY"
    )
    print(response)

Command Aliases Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following command aliases are available for convenience:

==========================  ================================================================
Command                     Aliases
==========================  ================================================================
get-access-token            gat
get-user-information        get-user-info, gui
create-project-api-token    create-api-token, cat
delete-project-api-token    delete-api-token, dat
update-project-api-token    update-api-token, uat
get-project-api-token       get-api-token, gat
==========================  ================================================================

Option Aliases Reference
~~~~~~~~~~~~~~~~~~~~~~~~~

The following option aliases are available for convenience:

==========================  ================================================================
Option                      Aliases
==========================  ================================================================
--project-id                --pid
--api-token-id              --tid
--name                      -n
--description               -d
--access-token              --token
--client-id                 --cid
--username                  -u
--password                  -p
--scope                     -s
==========================  ================================================================

Security Notes
~~~~~~~~~~~~~~

* API tokens must be managed using organization-level API tokens or GAM tokens
* Project API tokens cannot manage other API tokens
* Deleted tokens cannot be updated or reactivated
* Status values: 'active' (token can be used) or 'blocked' (token cannot be used)
