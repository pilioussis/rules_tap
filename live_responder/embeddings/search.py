import numpy as np
from colorama import Fore, Style, Back
from rules_tap.common import Config
from .common import load_db, get_embedding

def search_store(config: Config, prompt: str, n: int):
    idx, mapping = load_db(config)

    embedding = get_embedding(config, prompt)
    print("Searching store for similar chunks")
    distances, indices = idx.search(np.array([embedding], dtype=np.float32), k=n)
    for i in range(len(indices[0])):
        print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} Result: {i + 1}  Similarity: {round(distances[0][i], 4)} Chunk: {indices[0][i]} {Style.RESET_ALL}")
        print(f"{Style.DIM}{mapping[str(int(indices[0][i]))]}{Style.RESET_ALL}")

    return [mapping[str(int(idx))] for idx in indices[0]]