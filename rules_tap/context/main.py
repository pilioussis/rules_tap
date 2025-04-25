from .runtime_extraction.main import runtime_extraction
from rules_tap.common import Config, rm_dir

def get_context(config: Config):
	rm_dir(config.chunk_dir)
	rm_dir(config.runtime_dir)

	runtime_extraction(config)
    