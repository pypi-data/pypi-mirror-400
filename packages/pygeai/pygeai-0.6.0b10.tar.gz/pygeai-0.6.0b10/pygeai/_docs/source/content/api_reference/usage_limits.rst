Usage Limits
============

The Usage Limits module provides functionality to define, monitor, and manage usage limits for organizations and projects. This helps control costs, prevent overuse, and implement subscription-based access models.

This section covers:

* Setting organization and project usage limits
* Configuring hard and soft limits
* Managing renewal policies
* Monitoring usage

For each operation, you use the Low-Level Service Layer.

Overview
--------

Usage limits can be configured at two levels:

* **Organization Level**: Applies to the entire organization
* **Project Level**: Applies to specific projects within an organization

Limit Types:

* **Soft Limit**: Warning threshold that triggers notifications
* **Hard Limit**: Maximum allowed usage; requests blocked when exceeded
* **Subscription Types**: Freemium, Daily, Weekly, Monthly
* **Usage Units**: Requests (count) or Cost (dollars)

Organization Usage Limits
--------------------------

Set Organization Limit
~~~~~~~~~~~~~~~~~~~~~~~

Defines a new usage limit for an organization.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.organization.limits.clients import UsageLimitClient

    client = UsageLimitClient()
    
    usage_limit = {
        "subscriptionType": "Monthly",
        "usageUnit": "Cost",
        "softLimit": 800.0,
        "hardLimit": 1000.0,
        "renewalStatus": "Renewable"
    }
    
    result = client.set_organization_usage_limit(
        organization="org-uuid",
        usage_limit=usage_limit
    )
    
    print(f"Limit ID: {result['id']}")

**Parameters:**

* ``organization``: (Required) Organization UUID
* ``usage_limit``: (Required) Dictionary with:
  
  * ``subscriptionType``: "Freemium", "Daily", "Weekly", or "Monthly"
  * ``usageUnit``: "Requests" or "Cost"
  * ``softLimit``: Warning threshold (number)
  * ``hardLimit``: Maximum allowed (must be >= softLimit)
  * ``renewalStatus``: "Renewable" or "NonRenewable"


Get Latest Organization Limit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    latest = client.get_organization_latest_usage_limit(
        organization="org-uuid"
    )
    
    print(f"Soft limit: {latest['softLimit']}")
    print(f"Hard limit: {latest['hardLimit']}")
    print(f"Current usage: {latest.get('currentUsage', 0)}")


List All Organization Limits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    all_limits = client.get_all_usage_limits_from_organization(
        organization="org-uuid"
    )
    
    for limit in all_limits.get('limits', []):
        print(f"{limit['subscriptionType']}: {limit['hardLimit']} {limit['usageUnit']}")


Update Organization Hard Limit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    client.set_organization_hard_limit(
        organization="org-uuid",
        limit_id="limit-uuid",
        hard_limit=2000.0
    )


Update Organization Soft Limit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    client.set_organization_soft_limit(
        organization="org-uuid",
        limit_id="limit-uuid",
        soft_limit=1500.0
    )


Set Renewal Status
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    client.set_organization_renewal_status(
        organization="org-uuid",
        limit_id="limit-uuid",
        renewal_status="NonRenewable"
    )


Delete Organization Limit
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    client.delete_usage_limit_from_organization(
        organization="org-uuid",
        limit_id="limit-uuid"
    )


Project Usage Limits
--------------------

Set Project Limit
~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    usage_limit = {
        "subscriptionType": "Daily",
        "usageUnit": "Requests",
        "softLimit": 900,
        "hardLimit": 1000,
        "renewalStatus": "Renewable"
    }
    
    result = client.set_project_usage_limit(
        organization="org-uuid",
        project="project-uuid",
        usage_limit=usage_limit
    )


Get Latest Project Limit
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    latest = client.get_latest_usage_limit_from_project(
        organization="org-uuid",
        project="project-uuid"
    )


Get Active Project Limit
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    active = client.get_active_usage_limit_from_project(
        organization="org-uuid",
        project="project-uuid"
    )


Update Project Limits
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client = UsageLimitClient()
    
    # Update hard limit
    client.set_hard_limit_for_active_usage_limit_from_project(
        organization="org-uuid",
        project="project-uuid",
        limit_id="limit-uuid",
        hard_limit=5000
    )
    
    # Update soft limit
    client.set_soft_limit_for_active_usage_limit_from_project(
        organization="org-uuid",
        project="project-uuid",
        limit_id="limit-uuid",
        soft_limit=4000
    )
    
    # Update renewal status
    client.set_project_renewal_status(
        organization="org-uuid",
        project="project-uuid",
        limit_id="limit-uuid",
        renewal_status="Renewable"
    )


Complete Example
----------------

.. code-block:: python

    from pygeai.organization.limits.clients import UsageLimitClient

    client = UsageLimitClient()
    org_id = "your-org-uuid"
    project_id = "your-project-uuid"

    # Set monthly cost limit for organization
    org_limit = client.set_organization_usage_limit(
        organization=org_id,
        usage_limit={
            "subscriptionType": "Monthly",
            "usageUnit": "Cost",
            "softLimit": 800.0,
            "hardLimit": 1000.0,
            "renewalStatus": "Renewable"
        }
    )
    print(f"Organization limit set: {org_limit['id']}")

    # Set daily request limit for project
    project_limit = client.set_project_usage_limit(
        organization=org_id,
        project=project_id,
        usage_limit={
            "subscriptionType": "Daily",
            "usageUnit": "Requests",
            "softLimit": 900,
            "hardLimit": 1000,
            "renewalStatus": "Renewable"
        }
    )
    print(f"Project limit set: {project_limit['id']}")

    # Monitor usage
    active_limit = client.get_active_usage_limit_from_project(
        organization=org_id,
        project=project_id
    )
    
    current = active_limit.get('currentUsage', 0)
    soft = active_limit['softLimit']
    hard = active_limit['hardLimit']
    
    print(f"\nCurrent usage: {current}/{hard}")
    
    if current >= hard:
        print("⛔ Hard limit reached!")
    elif current >= soft:
        print("⚠️ Soft limit exceeded")
    else:
        remaining = hard - current
        print(f"✅ {remaining} units remaining")


Best Practices
--------------

Limit Configuration
~~~~~~~~~~~~~~~~~~~

* Set soft limits at 80-90% of hard limits
* Choose appropriate subscription types:
  
  * Daily: For development/testing
  * Monthly: For production
  * Freemium: For trial users

* Use "Cost" units for budget control
* Use "Requests" units for rate limiting

Monitoring
~~~~~~~~~~

* Check usage regularly (hourly/daily)
* Send alerts when approaching soft limits
* Log when hard limits are hit
* Track usage trends over time

Renewal Management
~~~~~~~~~~~~~~~~~~

* Use "Renewable" for ongoing subscriptions
* Use "NonRenewable" for one-time allocations
* Document renewal schedules
* Automate renewal processes

Hierarchy
~~~~~~~~~

* Organization limits apply to all projects
* Project limits can be more restrictive
* Lower limit takes precedence
* Monitor both levels


Error Handling
--------------

.. code-block:: python

    from pygeai.organization.limits.clients import UsageLimitClient
    from pygeai.core.common.exceptions import APIError

    client = UsageLimitClient()

    try:
        client.set_organization_usage_limit(
            organization="org-uuid",
            usage_limit={
                "subscriptionType": "Monthly",
                "usageUnit": "Cost",
                "softLimit": 1000.0,
                "hardLimit": 800.0  # Invalid: hard < soft
            }
        )
    except APIError as e:
        print(f"Invalid limit configuration: {e}")


Common Issues
~~~~~~~~~~~~~

**Hard Limit Less Than Soft Limit**

Hard limit must be >= soft limit.

**Invalid Subscription Type**

Must be one of: "Freemium", "Daily", "Weekly", "Monthly".

**Invalid Usage Unit**

Must be either "Requests" or "Cost".


Notes
-----

* Limits are enforced in real-time
* Usage resets based on subscription type (daily/weekly/monthly)
* Non-renewable limits don't reset
* Both organization and project limits are checked
* Deleting a limit removes all usage tracking
