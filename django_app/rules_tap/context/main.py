import shutil
from .runtime_extraction.main import runtime_extraction
from .runtime_extraction.config import Config
from rules_tap.common import CHUNK_DIR

def get_context():
	if CHUNK_DIR.exists():
		shutil.rmtree(CHUNK_DIR)

	CHUNK_DIR.mkdir(parents=True, exist_ok=True)

	config = Config(module_names=["/app/django_app/org"])

	runtime_extraction(config)
    