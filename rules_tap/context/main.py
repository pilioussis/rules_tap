from rules_tap.common import ContextConfig, rm_dir
from .runtime_extraction.main import runtime_extraction
from .file_extraction.main import file_extraction
from .sql_tables import get_schema_context


def get_context(config: ContextConfig):
	rm_dir(config.chunk_dir)
	rm_dir(config.runtime_dir)

	# runtime_extraction(config)
	get_schema_context(config)
	file_extraction(config)
