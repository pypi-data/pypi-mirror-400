from pygeai.core.embeddings.managers import EmbeddingsManager
from pygeai.core.embeddings.models import EmbeddingConfiguration
from pygeai.core.services.llm.model import Model
from pygeai.core.services.llm.providers import Provider

manager = EmbeddingsManager()

document_inputs = [
    "Machine learning is a subset of artificial intelligence",
    "Neural networks are inspired by the human brain"
]

configuration = EmbeddingConfiguration(
    inputs=document_inputs,
    model=f"{Provider.COHERE}/{Model.Cohere.EMBED_ENGLISH_V3_0}",
    input_type="search_document",
    timeout=600,
    cache=False
)

embeddings = manager.generate_embeddings(configuration)

print(f"Model: {embeddings.model}")
print(f"Input type: search_document")
print(f"Documents embedded: {len(embeddings.data)}")
print(f"Usage - Prompt tokens: {embeddings.usage.prompt_tokens}")
print(f"Usage - Total cost: ${embeddings.usage.total_cost} {embeddings.usage.currency}")

query_input = ["What is neural network?"]

query_configuration = EmbeddingConfiguration(
    inputs=query_input,
    model=f"{Provider.COHERE}/{Model.Cohere.EMBED_ENGLISH_V3_0}",
    input_type="search_query",
    timeout=600,
    cache=False
)

query_embeddings = manager.generate_embeddings(query_configuration)
print(f"\nQuery embedded with input_type: search_query")
print(f"Usage - Total cost: ${query_embeddings.usage.total_cost} {query_embeddings.usage.currency}")
