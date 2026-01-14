Evaluation
==========

The Evaluation module provides functionality to assess and measure the performance of AI assistants using datasets, evaluation plans, and system metrics. This is essential for ensuring quality, tracking improvements, and comparing different assistant configurations.

This section covers:

* Creating and managing evaluation datasets
* Defining evaluation plans with metrics
* Executing evaluations
* Analyzing evaluation results

For each operation, you have three implementation options:

* `Command Line`_
* `Low-Level Service Layer`_
* `High-Level Service Layer`_

Overview
--------

The evaluation workflow consists of:

1. **Datasets**: Collections of test cases with inputs and expected outputs
2. **Evaluation Plans**: Configurations specifying which assistant to evaluate, which dataset to use, and which metrics to apply
3. **System Metrics**: Predefined metrics (e.g., accuracy, relevance, coherence) with configurable weights
4. **Execution**: Running the evaluation plan against the dataset
5. **Results**: Detailed performance metrics and row-level analysis

Dataset Management
------------------

Create Dataset
~~~~~~~~~~~~~~

Creates a new evaluation dataset with test cases.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai evaluation create-dataset \
      --name "Customer Support QA" \
      --description "Test cases for customer support assistant" \
      --type "TextPromptAssistant"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

    client = EvaluationDatasetClient(eval_url="https://eval.saia.ai")
    
    dataset = client.create_dataset(
        dataset_name="Customer Support QA",
        dataset_description="Test cases for customer support assistant",
        dataset_type="TextPromptAssistant",
        dataset_active=True,
        rows=[
            {
                "dataSetRowInput": "How do I reset my password?",
                "dataSetRowExpectedOutput": "Click 'Forgot Password' on the login page..."
            }
        ]
    )
    print(dataset)

**Parameters:**

* ``dataset_name``: (Required) Name of the dataset
* ``dataset_description``: Description of the dataset's purpose
* ``dataset_type``: Type of assistant being evaluated (e.g., "TextPromptAssistant", "RAG Assistant")
* ``dataset_active``: Boolean indicating if dataset is active (default: True)
* ``rows``: Optional list of initial dataset rows

**Returns:**
Dictionary containing the created dataset with ID and metadata.

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

Currently uses the low-level client. Future versions may include a manager class.


Create Dataset from File
~~~~~~~~~~~~~~~~~~~~~~~~~

Uploads a dataset from a JSON file.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai evaluation create-dataset-from-file \
      --file-path "/path/to/dataset.json"

**File Format:**

.. code-block:: json

    {
        "dataSetName": "Customer Support QA",
        "dataSetDescription": "Test cases for customer support",
        "dataSetType": "TextPromptAssistant",
        "dataSetActive": true,
        "rows": [
            {
                "dataSetRowInput": "How do I reset my password?",
                "dataSetRowExpectedOutput": "Click 'Forgot Password'..."
            }
        ]
    }

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

    client = EvaluationDatasetClient(eval_url="https://eval.saia.ai")
    result = client.create_dataset_from_file(file_path="/path/to/dataset.json")
    print(result)

**Parameters:**

* ``file_path``: (Required) Path to JSON file containing dataset definition

**Returns:**
Dictionary with upload result and created dataset ID.


List Datasets
~~~~~~~~~~~~~

Retrieves all evaluation datasets.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai evaluation list-datasets

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.evaluation.dataset.clients import EvaluationDatasetClient

    client = EvaluationDatasetClient(eval_url="https://eval.saia.ai")
    datasets = client.list_datasets()
    
    for dataset in datasets.get('datasets', []):
        print(f"{dataset['dataSetId']}: {dataset['dataSetName']}")


Get Dataset
~~~~~~~~~~~

Retrieves a specific dataset by ID.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationDatasetClient(eval_url="https://eval.saia.ai")
    dataset = client.get_dataset(dataset_id="dataset-uuid")
    print(dataset)


Update Dataset
~~~~~~~~~~~~~~

Updates dataset metadata.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationDatasetClient(eval_url="https://eval.saia.ai")
    
    updated = client.update_dataset(
        dataset_id="dataset-uuid",
        dataset_name="Updated Name",
        dataset_description="Updated description",
        dataset_active=True
    )
    print(updated)


Delete Dataset
~~~~~~~~~~~~~~

Deletes a dataset.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationDatasetClient(eval_url="https://eval.saia.ai")
    result = client.delete_dataset(dataset_id="dataset-uuid")
    print(result)


Dataset Row Management
----------------------

Add Dataset Row
~~~~~~~~~~~~~~~

Adds a test case to an existing dataset.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationDatasetClient(eval_url="https://eval.saia.ai")
    
    row = client.create_dataset_row(
        dataset_id="dataset-uuid",
        row={
            "dataSetRowInput": "What are your business hours?",
            "dataSetRowExpectedOutput": "We are open Monday-Friday, 9am-5pm EST"
        }
    )
    print(row)


List Dataset Rows
~~~~~~~~~~~~~~~~~

Lists all rows in a dataset.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationDatasetClient(eval_url="https://eval.saia.ai")
    rows = client.list_dataset_rows(dataset_id="dataset-uuid")
    
    for row in rows.get('rows', []):
        print(f"Input: {row['dataSetRowInput']}")


Evaluation Plan Management
---------------------------

Create Evaluation Plan
~~~~~~~~~~~~~~~~~~~~~~

Creates an evaluation plan that defines which assistant to evaluate, which dataset to use, and which metrics to apply.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai evaluation create-plan \
      --name "Support Bot Evaluation v1" \
      --type "TextPromptAssistant" \
      --assistant-id "assistant-uuid" \
      --assistant-name "Support Bot" \
      --assistant-revision "1" \
      --dataset-id "dataset-uuid"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.evaluation.plan.clients import EvaluationPlanClient

    client = EvaluationPlanClient(eval_url="https://eval.saia.ai")
    
    plan = client.create_evaluation_plan(
        name="Support Bot Evaluation v1",
        type="TextPromptAssistant",
        assistant_id="assistant-uuid",
        assistant_name="Support Bot",
        assistant_revision="1",
        dataset_id="dataset-uuid",
        system_metrics=[
            {
                "systemMetricId": "metric-uuid-1",
                "systemMetricWeight": 0.6
            },
            {
                "systemMetricId": "metric-uuid-2",
                "systemMetricWeight": 0.4
            }
        ]
    )
    print(f"Created plan: {plan['evaluationPlanId']}")

**Parameters:**

* ``name``: (Required) Name of the evaluation plan
* ``type``: (Required) Assistant type ("TextPromptAssistant" or "RAG Assistant")
* ``assistant_id``: Assistant UUID (required for TextPromptAssistant)
* ``assistant_name``: Assistant name (required for TextPromptAssistant)
* ``assistant_revision``: Assistant revision number (required for TextPromptAssistant)
* ``profile_name``: RAG profile name (required for RAG Assistant)
* ``dataset_id``: UUID of the dataset to use
* ``system_metrics``: List of metrics with weights (weights should sum to 1.0)

**Returns:**
Dictionary containing the created evaluation plan with ID.


List System Metrics
~~~~~~~~~~~~~~~~~~~

Lists available system metrics that can be used in evaluation plans.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationPlanClient(eval_url="https://eval.saia.ai")
    metrics = client.list_system_metrics()
    
    for metric in metrics.get('systemMetrics', []):
        print(f"{metric['systemMetricName']}: {metric['systemMetricDescription']}")


Execute Evaluation Plan
~~~~~~~~~~~~~~~~~~~~~~~~

Executes an evaluation plan to assess assistant performance.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai evaluation execute-plan \
      --plan-id "plan-uuid"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationPlanClient(eval_url="https://eval.saia.ai")
    result = client.execute_evaluation_plan(evaluation_plan_id="plan-uuid")
    
    print(f"Execution started: {result['evaluationResultId']}")
    print(f"Status: {result['evaluationResultStatus']}")


List Evaluation Plans
~~~~~~~~~~~~~~~~~~~~~~

Lists all evaluation plans.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationPlanClient(eval_url="https://eval.saia.ai")
    plans = client.list_evaluation_plans()
    
    for plan in plans.get('evaluationPlans', []):
        print(f"{plan['evaluationPlanName']}: {plan['evaluationPlanType']}")


Get Evaluation Plan
~~~~~~~~~~~~~~~~~~~

Retrieves a specific evaluation plan.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationPlanClient(eval_url="https://eval.saia.ai")
    plan = client.get_evaluation_plan(evaluation_plan_id="plan-uuid")
    print(plan)


Evaluation Results
------------------

List Evaluation Results
~~~~~~~~~~~~~~~~~~~~~~~

Lists all results for a specific evaluation plan.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.evaluation.result.clients import EvaluationResultClient

    client = EvaluationResultClient(eval_url="https://eval.saia.ai")
    results = client.list_evaluation_results(evaluation_plan_id="plan-uuid")
    
    for result in results.get('evaluationResults', []):
        print(f"Result ID: {result['evaluationResultId']}")
        print(f"Status: {result['evaluationResultStatus']}")
        print(f"Cost: {result['evaluationResultCost']}")
        print(f"Duration: {result['evaluationResultDuration']}s")


Get Evaluation Result
~~~~~~~~~~~~~~~~~~~~~

Retrieves detailed results including row-level analysis.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    client = EvaluationResultClient(eval_url="https://eval.saia.ai")
    result = client.get_evaluation_result(evaluation_result_id="result-uuid")
    
    print(f"Overall Score: {result['evaluationResultScore']}")
    print(f"Total Cost: {result['evaluationResultCost']}")
    
    for row in result.get('rows', []):
        print(f"\nRow {row['dataSetRowId']}:")
        print(f"  Status: {row['evaluationResultRowStatus']}")
        print(f"  Score: {row['evaluationResultRowScore']}")
        print(f"  Output: {row['evaluationResultRowOutput']}")

**Note:** The API contains some field name typos (e.g., "evaluationResultAssitantRevision", "evaluationResultChunckCount"). These are returned as-is from the API.


Complete Workflow Example
--------------------------

.. code-block:: python

    from pygeai.evaluation.dataset.clients import EvaluationDatasetClient
    from pygeai.evaluation.plan.clients import EvaluationPlanClient
    from pygeai.evaluation.result.clients import EvaluationResultClient
    import time

    eval_url = "https://eval.saia.ai"

    dataset_client = EvaluationDatasetClient(eval_url=eval_url)
    dataset = dataset_client.create_dataset(
        dataset_name="Support Bot Test Cases",
        dataset_description="Common customer support questions",
        dataset_type="TextPromptAssistant",
        rows=[
            {
                "dataSetRowInput": "How do I reset my password?",
                "dataSetRowExpectedOutput": "Click 'Forgot Password' on login page"
            },
            {
                "dataSetRowInput": "What are your hours?",
                "dataSetRowExpectedOutput": "Monday-Friday, 9am-5pm EST"
            }
        ]
    )
    dataset_id = dataset['dataSetId']
    print(f"Created dataset: {dataset_id}")

    plan_client = EvaluationPlanClient(eval_url=eval_url)
    metrics = plan_client.list_system_metrics()
    metric_id = metrics['systemMetrics'][0]['systemMetricId']
    
    plan = plan_client.create_evaluation_plan(
        name="Support Bot v1 Evaluation",
        type="TextPromptAssistant",
        assistant_id="your-assistant-uuid",
        assistant_name="Support Bot",
        assistant_revision="1",
        dataset_id=dataset_id,
        system_metrics=[
            {"systemMetricId": metric_id, "systemMetricWeight": 1.0}
        ]
    )
    plan_id = plan['evaluationPlanId']
    print(f"Created plan: {plan_id}")

    execution = plan_client.execute_evaluation_plan(evaluation_plan_id=plan_id)
    result_id = execution['evaluationResultId']
    print(f"Started execution: {result_id}")

    result_client = EvaluationResultClient(eval_url=eval_url)
    
    while True:
        result = result_client.get_evaluation_result(evaluation_result_id=result_id)
        status = result['evaluationResultStatus']
        print(f"Status: {status}")
        
        if status in ['Completed', 'Failed']:
            break
        
        time.sleep(5)
    
    if status == 'Completed':
        print(f"\nEvaluation Complete!")
        print(f"Overall Score: {result['evaluationResultScore']}")
        print(f"Total Cost: ${result['evaluationResultCost']}")
        print(f"Duration: {result['evaluationResultDuration']}s")
        
        print("\nRow Results:")
        for row in result.get('rows', []):
            print(f"  - Score: {row['evaluationResultRowScore']}")


Best Practices
--------------

Dataset Design
~~~~~~~~~~~~~~

* Include diverse test cases covering common and edge cases
* Ensure expected outputs are clear and specific
* Use consistent formatting across rows
* Start with 20-50 test cases, expand based on results
* Version datasets alongside assistant versions

Metrics Selection
~~~~~~~~~~~~~~~~~

* Choose metrics aligned with your quality goals
* Weight metrics based on business priorities
* Test with different metric combinations
* Document why specific metrics were chosen

Evaluation Execution
~~~~~~~~~~~~~~~~~~~~

* Run evaluations regularly (e.g., before deploying new versions)
* Compare results across assistant revisions
* Track cost and duration trends
* Archive historical results for analysis

Error Handling
--------------

Common Issues
~~~~~~~~~~~~~

**Missing Evaluation URL**

.. code-block:: python

    from pygeai.core.common.exceptions import MissingRequirementException
    
    try:
        client = EvaluationDatasetClient()
    except MissingRequirementException as e:
        print("Set GEAI_EVAL_URL environment variable or pass eval_url parameter")

**Invalid Dataset Type**

Ensure ``dataset_type`` matches ``evaluation_plan_type`` and assistant type:
- "TextPromptAssistant" for chat/text assistants
- "RAG Assistant" for RAG assistants

**Metric Weights Don't Sum to 1.0**

When specifying multiple metrics, ensure weights sum to 1.0:

.. code-block:: python

    system_metrics=[
        {"systemMetricId": "metric-1", "systemMetricWeight": 0.6},
        {"systemMetricId": "metric-2", "systemMetricWeight": 0.4}
    ]

Notes
-----

* The Evaluation API requires a separate evaluation URL (``eval_url``)
* Set via ``GEAI_EVAL_URL`` environment variable or pass to client constructor
* Evaluation results are read-only; they cannot be modified or deleted
* Some API response fields contain typos (preserved for compatibility)
* Execution time depends on dataset size and assistant complexity
