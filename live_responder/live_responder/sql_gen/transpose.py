import re
from .config import EmbeddingConfig


def transpose_to_sandbox(config: EmbeddingConfig, statement_string: str):
	raw_function_call = "([[user_id]])"
	raw_schema_name_with_dot = f"{config.transpose_sql_schema_token}."

	pattern_schema_name = re.escape(raw_schema_name_with_dot)
	pattern = pattern_schema_name + r'([a-zA-Z_]*)' # Also allow underscores in table names

	replacement = raw_schema_name_with_dot + r'\1' + raw_function_call

	modified_statement = re.sub(pattern, replacement, statement_string)

	return modified_statement
	