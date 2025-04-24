import faiss
import numpy as np
import json
from openai import OpenAI
from django.conf import settings
from rules_tap.common import OUT_DIR

INDEX_PATH = OUT_DIR / 'hnsw_index.faiss'
MAPPING_PATH = OUT_DIR / 'id_to_text.json'

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    arr = response.data[0].embedding

    embedding = np.array(arr, dtype=np.float32)
    return embedding



def save_db(idx, mapping):
    faiss.write_index(idx, str(INDEX_PATH))
    with open(MAPPING_PATH, 'w', encoding='utf-8') as f:
        json.dump(mapping, f)


def load_db():
    if INDEX_PATH.exists():
        idx = faiss.read_index(str(INDEX_PATH))
        # TODO: I don't think this is necessary???
        if not isinstance(idx, faiss.IndexIDMap):
            idx = faiss.IndexIDMap(idx)
    else:
        base_index = faiss.IndexHNSWFlat(1536, 32)
        idx        = faiss.IndexIDMap(base_index)

    if MAPPING_PATH.exists():
        with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
    else:
        mapping = {}
    return idx, mapping
