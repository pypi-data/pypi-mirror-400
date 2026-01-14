Assistant Management
====================

The Assistant module provides functionality to create, manage, and interact with AI assistants in Globant Enterprise AI. Assistants can be of different types (chat, text, RAG) and are configured with specific prompts, LLM settings, and behaviors.

This section covers:

* Creating assistants (chat, text, RAG)
* Retrieving assistant information
* Updating assistant configuration
* Deleting assistants
* Sending chat requests to assistants
* Managing assistant requests

For each operation, you have three implementation options:

* `Command Line`_
* `Low-Level Service Layer`_
* `High-Level Service Layer`_


Create Chat Assistant
~~~~~~~~~~~~~~~~~~~~~

Creates a new chat assistant with specified configuration including LLM settings, welcome data, and guardrails.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai assistant create \
      --type chat \
      --name "Customer Support Bot" \
      --prompt "You are a helpful customer support assistant"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.clients import AssistantClient

    client = AssistantClient()
    
    response = client.create_assistant(
        assistant_type="chat",
        name="Customer Support Bot",
        prompt="You are a helpful customer support assistant",
        description="Handles customer inquiries"
    )
    print(response)

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager
    from pygeai.core.models import ChatAssistant, LlmSettings
    from pygeai.core.services.llm.model import Model
    from pygeai.core.services.llm.providers import Provider

    manager = AssistantManager()

    llm_settings = LlmSettings(
        provider_name=Provider.OPENAI,
        model_name=Model.OpenAI.GPT_4,
        temperature=0.7,
        max_tokens=1000
    )

    assistant = ChatAssistant(
        name="Customer Support Bot",
        description="Handles customer inquiries",
        prompt="You are a helpful customer support assistant",
        llm_settings=llm_settings
    )

    response = manager.create_assistant(assistant)
    print(f"Response: {response}")


Get Assistant Data
~~~~~~~~~~~~~~~~~~

Retrieves information about a specific assistant.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai assistant get-assistant --detail full

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.clients import AssistantClient

    client = AssistantClient()
    
    assistant_data = client.get_assistant_data(
        assistant_id="assistant-uuid",
        detail="full"
    )
    print(assistant_data)

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager

    manager = AssistantManager()
    
    assistant = manager.get_assistant_data(
        assistant_id="assistant-uuid",
        detail="full"
    )
    print(f"Assistant: {assistant}")


Update Assistant
~~~~~~~~~~~~~~~~

Updates an existing assistant's configuration.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai assistant update \
      --name "Customer Support Bot" \
      --prompt "You are an expert customer support assistant"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.clients import AssistantClient

    client = AssistantClient()
    
    response = client.update_assistant(
        assistant_id="assistant-uuid",
        prompt="You are an expert customer support assistant"
    )
    print(response)

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager
    from pygeai.core.models import ChatAssistant

    manager = AssistantManager()
    
    assistant = manager.get_assistant_data(assistant_id="assistant-uuid")
    assistant.prompt = "You are an expert customer support assistant"
    
    response = manager.update_assistant(
        assistant=assistant,
        action="saveNewRevision"
    )
    print(f"Response: {response}")


Delete Assistant
~~~~~~~~~~~~~~~~

Deletes an assistant from the system.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai assistant delete --name "Customer Support Bot"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.clients import AssistantClient

    client = AssistantClient()
    
    response = client.delete_assistant(assistant_id="assistant-uuid")
    print(response)

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager

    manager = AssistantManager()
    
    response = manager.delete_assistant(assistant_id="assistant-uuid")
    print(f"Response: {response}")


Send Chat Request
~~~~~~~~~~~~~~~~~

Sends a chat message to an assistant and receives a response.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai assistant chat \
      --name "Customer Support Bot" \
      --msg '[{"role": "user", "content": "Hello, I need help"}]'

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.clients import AssistantClient

    client = AssistantClient()
    
    messages = [
        {"role": "user", "content": "Hello, I need help"}
    ]
    
    response = client.send_chat_request(
        assistant_name="Customer Support Bot",
        messages=messages
    )
    print(response)

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager
    from pygeai.core.models import ChatMessageList, ChatMessage

    manager = AssistantManager()
    
    messages = ChatMessageList(
        messages=[
            ChatMessage(role="user", "Hello, I need help")
        ]
    )
    
    response = manager.chat_completion(
        assistant_name="Customer Support Bot",
        messages=messages
    )
    print(f"Response: {response}")


Get Request Status
~~~~~~~~~~~~~~~~~~

Checks the status of an asynchronous assistant request.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.clients import AssistantClient

    client = AssistantClient()
    
    status = client.get_request_status(request_id="request-uuid")
    print(status)

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager

    manager = AssistantManager()
    
    status = manager.get_request_status(request_id="request-uuid")
    print(f"Status: {status}")


Cancel Request
~~~~~~~~~~~~~~

Cancels a pending assistant request.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.clients import AssistantClient

    client = AssistantClient()
    
    response = client.cancel_request(request_id="request-uuid")
    print(response)

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager

    manager = AssistantManager()
    
    response = manager.cancel_request(request_id="request-uuid")
    print(f"Response: {response}")
