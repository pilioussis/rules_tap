import shutil
from .runtime_extraction.main import runtime_extraction
from rules_tap.common import CHUNK_DIR

def get_context():
	if CHUNK_DIR.exists():
		shutil.rmtree(CHUNK_DIR)

	CHUNK_DIR.mkdir(parents=True, exist_ok=True)
	runtime_extraction()
    