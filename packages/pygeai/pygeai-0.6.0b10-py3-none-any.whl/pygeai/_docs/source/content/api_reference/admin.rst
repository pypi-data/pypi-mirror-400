Administration
==============

The Admin module provides administrative functionality for managing organizations, projects, and API tokens in Globant Enterprise AI. This module is primarily used for validation, authorization checks, and retrieving project information.

This section covers:

* Validating API tokens
* Getting authorized organizations
* Getting authorized projects
* Retrieving project API tokens
* Checking project visibility

For each operation, you have two implementation options:

* `Command Line`_
* `Low-Level Service Layer`_

.. note::
   The Admin module currently does not have a High-Level Service Layer (Manager class).


Validate API Token
~~~~~~~~~~~~~~~~~~

Validates an API token and returns information about the organization and project it belongs to.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai admin validate-token

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.admin.clients import AdminClient

    client = AdminClient()
    
    result = client.validate_api_token()
    print(result)


Get Authorized Organizations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieves a list of organizations that the current user is authorized to access.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai admin get-orgs

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.admin.clients import AdminClient

    client = AdminClient()
    
    organizations = client.get_authorized_organizations()
    print(organizations)


Get Authorized Projects by Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieves a list of projects within a specific organization that the current user can access.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai admin get-projects --org "my-organization"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.admin.clients import AdminClient

    client = AdminClient()
    
    projects = client.get_authorized_projects_by_organization(
        organization="my-organization"
    )
    print(projects)


Get Project API Token
~~~~~~~~~~~~~~~~~~~~~

Retrieves the API token for a specific project using an access token.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai admin get-project-api-token \
      --org "my-organization" \
      --project "my-project" \
      --access-token "your-access-token"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.admin.clients import AdminClient

    client = AdminClient()
    
    api_token = client.get_project_api_token(
        organization="my-organization",
        project="my-project",
        access_token="your-access-token"
    )
    print(api_token)


Get Project Visibility
~~~~~~~~~~~~~~~~~~~~~~

Checks the visibility settings of a specific project.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai admin get-project-visibility \
      --org "my-organization" \
      --project "my-project" \
      --access-token "your-access-token"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.admin.clients import AdminClient

    client = AdminClient()
    
    visibility = client.get_project_visibility(
        organization="my-organization",
        project="my-project",
        access_token="your-access-token"
    )
    print(visibility)
