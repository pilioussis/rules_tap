import hashlib
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / 'out/context'
CHUNK_DIR = OUT_DIR / 'chunks'

def get_hash(text: str) -> int:
    hash_obj = hashlib.md5(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()[:8]
    hash_id = int.from_bytes(hash_bytes, byteorder='big', signed=False)
    return hash_id