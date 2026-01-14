from pygeai.core.embeddings.managers import EmbeddingsManager
from pygeai.core.embeddings.models import EmbeddingConfiguration
from pygeai.core.services.llm.model import Model
from pygeai.core.services.llm.providers import Provider
import numpy as np

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

manager = EmbeddingsManager()

texts = [
    "The cat sits on the mat",
    "A feline rests on a rug",
    "Python is a programming language"
]

configuration = EmbeddingConfiguration(
    inputs=texts,
    model=f"{Provider.OPENAI}/{Model.OpenAI.TEXT_EMBEDDING_3_SMALL}",
)

embeddings = manager.generate_embeddings(configuration)

embedding_vectors = [emb.embedding for emb in embeddings.data]

print("Cosine Similarity Matrix:")
print("=" * 60)
for i, text1 in enumerate(texts):
    for j, text2 in enumerate(texts):
        if i <= j:
            similarity = cosine_similarity(embedding_vectors[i], embedding_vectors[j])
            print(f"\nText {i+1} vs Text {j+1}: {similarity:.4f}")
            if i != j:
                print(f"  '{text1[:40]}...'")
                print(f"  '{text2[:40]}...'")

print(f"\n{'='*60}")
print(f"Total cost: ${embeddings.usage.total_cost} {embeddings.usage.currency}")
