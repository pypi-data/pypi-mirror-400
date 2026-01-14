from pygeai.core.embeddings.managers import EmbeddingsManager
from pygeai.core.embeddings.models import EmbeddingConfiguration
from pygeai.core.services.llm.model import Model
from pygeai.core.services.llm.providers import Provider

manager = EmbeddingsManager()

inputs = [
    "The quick brown fox jumps over the lazy dog",
    "Python is a high-level programming language"
]

configuration = EmbeddingConfiguration(
    inputs=inputs,
    model=f"{Provider.OPENAI}/{Model.OpenAI.TEXT_EMBEDDING_3_SMALL}",
    encoding_format="float",
    dimensions=1536,
    user=None,
    input_type=None,
    timeout=600,
    cache=False
)

embeddings = manager.generate_embeddings(configuration)

print(f"Model: {embeddings.model}")
print(f"Total embeddings generated: {len(embeddings.data)}")
print(f"Embedding dimensions: {len(embeddings.data[0].embedding)}")
print(f"Usage - Prompt tokens: {embeddings.usage.prompt_tokens}")
print(f"Usage - Total cost: ${embeddings.usage.total_cost} {embeddings.usage.currency}")
