import re
from live_responder.config import EmbeddingConfig

# This assumes Metabase's parameter syntax
FUNCTION_CALL_PARAMS = "({{user_id}})"

def transpose_to_sandbox(config: EmbeddingConfig, statement_string: str):
	""" This function converts the sql query from tables the user doesn't have access to, to function
	that are in the safe AI sandbox.

	e.g the table `ai_sandbox.org_worker` will be translated to `ai_sandbox.org_worker([[user_id]])`

	The function call will scope the returned rows to those that the user will have access to.
	"""
	
	raw_schema_name_with_dot = f"{config.transpose_sql_schema_token}."

	pattern_schema_name = re.escape(raw_schema_name_with_dot)
	pattern = pattern_schema_name + r'([a-zA-Z_]*)' # Also allow underscores in table names

	replacement = raw_schema_name_with_dot + r'\1' + FUNCTION_CALL_PARAMS

	modified_statement = re.sub(pattern, replacement, statement_string)

	return modified_statement
	