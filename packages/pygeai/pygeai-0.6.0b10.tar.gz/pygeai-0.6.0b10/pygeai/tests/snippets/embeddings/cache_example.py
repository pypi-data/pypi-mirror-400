from pygeai.core.embeddings.managers import EmbeddingsManager
from pygeai.core.embeddings.models import EmbeddingConfiguration
from pygeai.core.services.llm.model import Model
from pygeai.core.services.llm.providers import Provider
import time

manager = EmbeddingsManager()

inputs = ["This text will be cached for faster repeated access"]

configuration = EmbeddingConfiguration(
    inputs=inputs,
    model=f"{Provider.OPENAI}/{Model.OpenAI.TEXT_EMBEDDING_3_SMALL}",
    cache=True
)

print("First request (not cached)...")
start = time.time()
embeddings1 = manager.generate_embeddings(configuration)
elapsed1 = time.time() - start
print(f"Time: {elapsed1:.3f}s")
print(f"Cost: ${embeddings1.usage.total_cost} {embeddings1.usage.currency}")

print("\nSecond request (should be cached)...")
start = time.time()
embeddings2 = manager.generate_embeddings(configuration)
elapsed2 = time.time() - start
print(f"Time: {elapsed2:.3f}s")
print(f"Cost: ${embeddings2.usage.total_cost} {embeddings2.usage.currency}")

print(f"\nCache speedup: {elapsed1/elapsed2:.2f}x faster")
