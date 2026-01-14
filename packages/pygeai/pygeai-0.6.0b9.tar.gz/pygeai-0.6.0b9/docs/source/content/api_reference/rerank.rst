Reranking
=========

The Rerank module provides functionality to reorder document chunks based on their relevance to a query. This is particularly useful in retrieval-augmented generation (RAG) systems to prioritize the most relevant context.

This section covers:

* Reranking document chunks based on relevance
* Selecting top-N most relevant documents

For each operation, you have two implementation options:

* `Command Line`_
* `Low-Level Service Layer`_

.. note::
   The Rerank module currently does not have a High-Level Service Layer (Manager class).


Rerank Chunks
~~~~~~~~~~~~~

Reranks a list of document chunks based on their relevance to a given query.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai rerank rerank-chunks \
      --query "What is machine learning?" \
      --documents '["Machine learning is a subset of AI", "Python is a programming language", "Deep learning uses neural networks"]' \
      --model "cohere/rerank-english-v3.0" \
      --top-n 2

Using the alias:

.. code-block:: shell

    geai rerank chunks \
      -q "What is machine learning?" \
      -d "Machine learning is a subset of AI" \
      --top-n 2

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.rerank.clients import RerankClient

    client = RerankClient()
    
    query = "What is machine learning?"
    documents = [
        "Machine learning is a subset of AI",
        "Python is a programming language",
        "Deep learning uses neural networks"
    ]
    
    results = client.rerank_chunks(
        query=query,
        documents=documents,
        model="cohere/rerank-english-v3.0",
        top_n=2
    )
    print(results)

Example response:

.. code-block:: json

    {
        "results": [
            {
                "index": 0,
                "document": "Machine learning is a subset of AI",
                "relevance_score": 0.95
            },
            {
                "index": 2,
                "document": "Deep learning uses neural networks",
                "relevance_score": 0.72
            }
        ]
    }

Parameters
^^^^^^^^^^

* **query** (required): The search query to rank documents against
* **documents** (required): List of document strings to rerank
* **model** (optional): The reranking model to use (default: "cohere/rerank-english-v3.0")
* **top_n** (optional): Number of top results to return (default: returns all)
