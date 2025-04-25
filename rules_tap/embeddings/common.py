import faiss
import numpy as np
import json
from openai import OpenAI
from django.conf import settings
from rules_tap.common import Config


def get_embedding(config: Config, text: str):
    client = OpenAI(
        api_key=config.open_api_key,
    )
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    arr = response.data[0].embedding

    embedding = np.array(arr, dtype=np.float32)
    return embedding


def save_db(config: Config, idx, mapping):
    faiss.write_index(idx, str(config.vector_index_file))
    with open(config.id_to_text_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f)

def init_db():
    base_index = faiss.IndexHNSWFlat(1536, 32)
    idx        = faiss.IndexIDMap(base_index)
    return idx, {}

def load_db(config: Config):
    if not config.vector_index_file.exists():
        raise Exception(f"Vector index file {config.vector_index_file} does not exist")

    if not config.id_to_text_file.exists():
        raise Exception(f"ID to text file {config.id_to_text_file} does not exist")
    
    idx = faiss.read_index(str(config.vector_index_file))
    # TODO: I don't think this is necessary???
    if not isinstance(idx, faiss.IndexIDMap):
        idx = faiss.IndexIDMap(idx)
    
    with open(config.id_to_text_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    return idx, mapping
