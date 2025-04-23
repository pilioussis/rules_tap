# -*- coding: utf-8 -*-
from decimal import Decimal
import os
import openai
import faiss
import numpy as np
from django.conf import settings
from rules_tap.context.main import get_context
from rules_tap.context.logger import OUTPUT_DIR

from openai import OpenAI
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)

def save_to_store():
    query_dir = OUTPUT_DIR / 'query/'
    index = faiss.IndexHNSWFlat(1536, 32)  # Assuming 512-dimensional embeddings

    for filename in os.listdir(query_dir):
        with open(os.path.join(query_dir, filename), 'r', encoding='utf-8') as file:
            text = file.read()
            print(text)
            response = client.embeddings.create(
                input="Your text string goes here",
                model="text-embedding-3-small"
            )
            arr = response.data[0].embedding

            embedding = np.array(arr, dtype=np.float32)
            index.add(np.array([embedding]))

    faiss.write_index(index, str(OUTPUT_DIR / 'hnsw_index.faiss'))

    