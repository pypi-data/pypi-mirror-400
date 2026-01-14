Proxy
=====

The Proxy module enables tool proxying functionality, allowing external tools and services to be registered and made available to AI assistants. This creates a bridge between GEAI assistants and external APIs or custom functions.

This section covers:

* Registering tool proxies
* Submitting jobs to proxies
* Monitoring job execution
* Retrieving results

For each operation, you use the Low-Level Service Layer.

Overview
--------

The proxy system enables:

* **Tool Registration**: Register external tools with the system
* **Job Submission**: Submit work to registered tools
* **Async Execution**: Tools process jobs asynchronously
* **Result Retrieval**: Poll for and retrieve job results
* **Server Deployment**: Run proxy servers to handle tool execution

Architecture:

1. Register tools with proxy
2. Assistant requests tool execution
3. Job submitted to proxy
4. Proxy routes to appropriate tool/server
5. Results returned to assistant

Tool Proxy Registration
-----------------------

Register a Proxy
~~~~~~~~~~~~~~~~

.. code-block:: python

    from pygeai.proxy.clients import ToolProxyData, ProxiedTool
    import uuid

    # Define a tool
    tool = ProxiedTool(
        name="weather_lookup",
        description="Get current weather for a location",
        server_name="weather-server",
        input_schema={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["location"]
        }
    )

    # Create proxy registration
    proxy_data = ToolProxyData(
        id=uuid.uuid4(),
        name="Weather Tools",
        description="Weather information tools",
        affinity=uuid.uuid4(),
        tools=[tool]
    )

    # Register (implementation depends on proxy client setup)
    # proxy_client.register(proxy_data)

**Components:**

* ``ToolProxyData``: Proxy registration information
* ``ProxiedTool``: Individual tool definition
* ``input_schema``: JSON Schema for tool parameters

Job Management
--------------

Submit Job
~~~~~~~~~~

.. code-block:: python

    from pygeai.proxy.clients import ToolProxyJob

    # Job submission (conceptual - actual implementation may vary)
    job = {
        "proxy_id": "proxy-uuid",
        "tool_name": "weather_lookup",
        "input": {
            "location": "San Francisco"
        }
    }

    # Submit job to proxy
    # result = proxy_client.submit_job(job)


Check Job Status
~~~~~~~~~~~~~~~~

.. code-block:: python

    from pygeai.proxy.clients import ToolProxyJob

    # Poll for job completion
    job = ToolProxyJob(
        id=uuid.UUID("job-uuid"),
        proxy_id=uuid.UUID("proxy-uuid"),
        proxy_status="active",
        job_status="pending"
    )

    # Check status
    # status = proxy_client.get_job_status(job.id)


Get Job Result
~~~~~~~~~~~~~~

.. code-block:: python

    from pygeai.proxy.clients import ToolProxyJobResult

    # Retrieve completed job result
    result = ToolProxyJobResult(
        success=True,
        job=job  # ToolProxyJob instance
    )

    if result.success:
        output = result.job.output
        print(f"Result: {output}")


Proxy Server
------------

The proxy module includes server functionality to handle tool execution:

.. code-block:: python

    from pygeai.proxy.servers import ProxyServer
    from pygeai.proxy.config import ProxyConfig

    # Configure proxy server
    config = ProxyConfig(
        host="localhost",
        port=8080,
        # Additional configuration...
    )

    # Start server
    server = ProxyServer(config)
    server.start()

**Note:** Server deployment typically runs as a separate service.


Complete Example
----------------

.. code-block:: python

    from pygeai.proxy.clients import ToolProxyData, ProxiedTool
    from pygeai.proxy.tool import ProxiedTool
    import uuid

    # Define tools
    calculator_tool = ProxiedTool(
        name="calculate",
        description="Perform mathematical calculations",
        server_name="calc-server",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {"type": "string"},
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]}
            }
        }
    )

    database_tool = ProxiedTool(
        name="query_db",
        description="Query customer database",
        server_name="db-server",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer"}
            }
        }
    )

    # Create proxy with multiple tools
    proxy = ToolProxyData(
        id=uuid.uuid4(),
        name="Business Tools",
        description="Tools for business operations",
        tools=[calculator_tool, database_tool]
    )

    print(f"Proxy configuration: {proxy.to_dict()}")


Tool Definition Schema
----------------------

Required Fields
~~~~~~~~~~~~~~~

* ``name``: Unique tool identifier
* ``description``: Human-readable description
* ``server_name``: Server handling this tool
* ``input_schema``: JSON Schema for parameters

Input Schema Format
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    input_schema = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "First parameter",
                "enum": ["option1", "option2"]  # Optional
            },
            "param2": {
                "type": "integer",
                "description": "Second parameter",
                "minimum": 0,  # Optional constraints
                "maximum": 100
            }
        },
        "required": ["param1"]
    }


Best Practices
--------------

Tool Design
~~~~~~~~~~~

* Use clear, descriptive tool names
* Provide detailed descriptions
* Define complete input schemas
* Include parameter descriptions
* Specify required vs optional parameters
* Add validation constraints

Security
~~~~~~~~

* Validate all input parameters
* Sanitize user inputs
* Implement authentication
* Use HTTPS for communication
* Rate limit tool usage
* Log all tool executions

Error Handling
~~~~~~~~~~~~~~

* Return clear error messages
* Include error codes
* Handle timeouts gracefully
* Implement retry logic
* Log failures for debugging

Performance
~~~~~~~~~~~

* Optimize tool execution time
* Implement caching where appropriate
* Use async processing
* Monitor resource usage
* Scale servers based on load


Integration with Assistants
----------------------------

Tools registered via proxy can be made available to assistants:

.. code-block:: python

    # Register proxy with tools
    # ...

    # Configure assistant to use proxied tools
    # (Specific integration depends on assistant configuration)

    # Assistant can now call:
    # "Get the weather in Tokyo"
    # -> Routes to weather_lookup tool
    # -> Returns weather data


Notes
-----

* Proxies enable extensibility of assistant capabilities
* Tools execute asynchronously
* Affinity groups related tools
* Public vs private tool visibility options
* Server handles actual tool execution
* Input schemas use JSON Schema specification
* Tool responses should be JSON-serializable

For detailed proxy architecture, see ``docs/geai-proxy/README.md``.
