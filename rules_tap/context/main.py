from rules_tap.common import ContextConfig, rm_dir
from .runtime_extraction.main import runtime_extraction
from .file_extraction.main import file_extraction
from .sql_tables import get_schema_context


def get_context(config: ContextConfig):
	"""Gets context from all sources and saves it in config.context_dir"""
	# Clean any old build artifacts
	rm_dir(config.chunk_dir)
	rm_dir(config.runtime_dir)

	# Compile context from each source
	runtime_extraction(config)
	get_schema_context(config)
	file_extraction(config)
