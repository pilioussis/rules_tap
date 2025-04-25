import numpy as np
from rules_tap.common import Config
from .common import load_db, get_embedding

def search_store(config: Config, prompt: str):
    idx, mapping = load_db(config)

    embedding = get_embedding(config, prompt)
    distances, indices = idx.search(np.array([embedding], dtype=np.float32), k=1)
    for i in range(len(indices[0])):
        print(distances[0][i], indices[0][i], mapping[str(int(indices[0][i]))][:100])

    return [mapping[str(int(idx))] for idx in indices[0]]