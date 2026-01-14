from pygeai.core.embeddings.managers import EmbeddingsManager
from pygeai.core.embeddings.models import EmbeddingConfiguration
from pygeai.core.services.llm.model import Model
from pygeai.core.services.llm.providers import Provider

manager = EmbeddingsManager()

inputs = ["Text to embed with base64 encoding"]

configuration = EmbeddingConfiguration(
    inputs=inputs,
    model=f"{Provider.OPENAI}/{Model.OpenAI.TEXT_EMBEDDING_3_SMALL}",
    encoding_format="base64",
    dimensions=512,
    user=None,
    input_type=None,
    timeout=600,
    cache=False
)

embeddings = manager.generate_embeddings(configuration)

print(f"Model: {embeddings.model}")
print(f"Encoding format: base64")
print(f"Embedding (base64 encoded, first 100 chars): {embeddings.data[0].embedding[:100]}")
print(f"Type of embedding: {type(embeddings.data[0].embedding)}")
print(f"Usage - Total cost: ${embeddings.usage.total_cost} {embeddings.usage.currency}")
