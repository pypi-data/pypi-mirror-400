Health & Status
===============

The Health module provides functionality to check the operational status of Globant Enterprise AI services and endpoints.

This section covers:

* Checking API health status
* Verifying service availability

For each operation, you have two implementation options:

* `Command Line`_
* `Low-Level Service Layer`_

.. note::
   The Health module currently does not have a High-Level Service Layer (Manager class).


Check API Status
~~~~~~~~~~~~~~~~

Checks the health and availability of the Globant Enterprise AI API.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai status

Or using the alias:

.. code-block:: shell

    geai s

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.health.clients import HealthClient

    client = HealthClient()
    
    status = client.get_health()
    print(status)

Example response:

.. code-block:: json

    {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2026-01-06T12:00:00Z"
    }
