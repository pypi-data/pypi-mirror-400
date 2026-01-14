Feedback
========

The Feedback module allows you to collect and submit user feedback for assistant responses. This helps track response quality, identify areas for improvement, and train better models.

Overview
--------

Feedback enables you to:

* Submit ratings for assistant responses (good/bad)
* Add optional comments for context
* Track feedback via request IDs
* Analyze response quality over time

Send Feedback
-------------

Submits feedback for a specific assistant response.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai feedback send \
      --request-id "request-uuid" \
      --score 1 \
      --comments "Very helpful response"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.feedback.clients import FeedbackClient

    client = FeedbackClient()
    
    result = client.send_feedback(
        request_id="request-uuid",
        answer_score=1,
        comments="Very helpful and accurate response"
    )
    
    print("Feedback submitted successfully")

**Parameters:**

* ``request_id``: (Required) The request ID from the assistant execution
* ``origin``: Feedback origin (default: "user-feedback")
* ``answer_score``: (Required) Score indicating quality:
  
  * ``1``: Good response
  * ``2``: Bad response

* ``comments``: Optional text feedback/explanation

**Returns:**
Dictionary confirming feedback submission (typically empty JSON ``{}``)


Complete Example
----------------

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager
    from pygeai.core.feedback.clients import FeedbackClient
    from pygeai.core.models import ChatMessageList, ChatMessage

    # Send a chat request
    assistant_manager = AssistantManager()
    
    messages = ChatMessageList(
        messages=[
            ChatMessage(role="user", content="What is the capital of France?")
        ]
    )
    
    response = assistant_manager.chat_completion(
        assistant_name="Geography Assistant",
        messages=messages
    )
    
    request_id = response.request_id
    answer = response.content
    
    print(f"Assistant: {answer}")

    # Collect user feedback
    user_rating = input("Was this helpful? (y/n): ")
    user_comment = input("Additional feedback (optional): ")
    
    # Submit feedback
    feedback_client = FeedbackClient()
    
    feedback_client.send_feedback(
        request_id=request_id,
        answer_score=1 if user_rating.lower() == 'y' else 2,
        comments=user_comment if user_comment else None
    )
    
    print("Thank you for your feedback!")


Best Practices
--------------

Collection Strategy
~~~~~~~~~~~~~~~~~~~

* Collect feedback at appropriate moments
* Don't interrupt critical user workflows
* Make feedback optional, not mandatory
* Use simple rating mechanisms
* Allow optional detailed comments

Request ID Tracking
~~~~~~~~~~~~~~~~~~~

* Always capture and store request IDs
* Associate request IDs with user sessions
* Track which responses received feedback
* Monitor feedback completion rates

Feedback Quality
~~~~~~~~~~~~~~~~

* Provide clear rating options
* Explain what "good" and "bad" mean
* Encourage specific comments
* Follow up on negative feedback
* Thank users for providing feedback


Integration Patterns
--------------------

Inline Feedback
~~~~~~~~~~~~~~~

.. code-block:: python

    from pygeai.assistant.managers import AssistantManager
    from pygeai.core.feedback.clients import FeedbackClient

    def chat_with_feedback(assistant_name, user_message):
        # Get assistant response
        manager = AssistantManager()
        response = manager.chat_completion(
            assistant_name=assistant_name,
            messages=[{"role": "user", "content": user_message}]
        )
        
        print(f"Assistant: {response.content}")
        
        # Prompt for immediate feedback
        rating = input("Rate this response (1=good, 2=bad): ")
        
        if rating in ['1', '2']:
            feedback_client = FeedbackClient()
            feedback_client.send_feedback(
                request_id=response.request_id,
                answer_score=int(rating)
            )
        
        return response

Batch Feedback
~~~~~~~~~~~~~~

.. code-block:: python

    from pygeai.core.feedback.clients import FeedbackClient

    # Collect feedback for multiple requests
    feedback_queue = [
        {"request_id": "req-1", "score": 1, "comments": "Great!"},
        {"request_id": "req-2", "score": 2, "comments": "Inaccurate"},
        {"request_id": "req-3", "score": 1, "comments": None}
    ]

    client = FeedbackClient()
    
    for item in feedback_queue:
        try:
            client.send_feedback(
                request_id=item["request_id"],
                answer_score=item["score"],
                comments=item["comments"]
            )
            print(f"Submitted feedback for {item['request_id']}")
        except Exception as e:
            print(f"Failed to submit feedback: {e}")


Error Handling
--------------

.. code-block:: python

    from pygeai.core.feedback.clients import FeedbackClient
    from pygeai.core.common.exceptions import APIError

    client = FeedbackClient()

    try:
        client.send_feedback(
            request_id="invalid-request-id",
            answer_score=1
        )
    except APIError as e:
        print(f"Failed to submit feedback: {e}")
        # Log error for later retry


Common Issues
~~~~~~~~~~~~~

**Invalid Request ID**

Ensure the request ID is valid and from a recent assistant execution.

**Invalid Score Value**

Score must be exactly ``1`` (good) or ``2`` (bad).


Notes
-----

* Feedback is associated with specific assistant requests
* The origin parameter should typically remain "user-feedback"
* Comments are optional but provide valuable context
* Feedback data can be used for assistant improvement
* Request IDs expire after a certain period (check your configuration)
