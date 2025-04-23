from rules_tap.context.logger import OUTPUT_DIR
import faiss
import numpy as np
from .common import client

def search_store(prompt):
    index = faiss.read_index(str(OUTPUT_DIR / 'hnsw_index.faiss'))
    response = client.embeddings.create(
        input=prompt,
        model="text-embedding-3-small"
    )
    arr = response.data[0].embedding
    D, I = index.search(np.array([arr], dtype=np.float32), k=10)
    return I