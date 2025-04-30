from datetime import datetime
from django.core.management import call_command
from pathlib import Path
from rules_tap.common import ContextConfig
from .create_functions import create_functions


def create_migration(config: ContextConfig):
	"""
	Creates a new migration in config.migrations_app that will:
		- Drop the existing sandbox
		- Recreate sandbox functions
		- Assign permission to the sandbox user
	"""
	
	migration_file = create_empty_migration(config)

	migration_statements = get_migration_statements(config)

	write_migration_statements(migration_file, migration_statements)


def create_empty_migration(config: ContextConfig):
	migration_name = f"sandbox_ai_{datetime.now().strftime('%Y%m%d%H%M%S')}"
	call_command('makemigrations', config.migrations_app.label, empty=True, name=migration_name)

	migration_file = get_migration_file(config, migration_name)
	
	return migration_file

def get_migration_file(config: ContextConfig, migration_name: str):
	migration_file_glob = f"*{migration_name}.py"
	migration_file = next(Path(config.migrations_app.path).glob(f'migrations/{migration_file_glob}'))

	if not migration_file.exists():
		raise Exception(f'Migration file not at: {migration_file}')

	return migration_file


def get_migration_statements(config: ContextConfig) -> list[str]:
	house_keeping_statements = [
		'DROP SCHEMA IF EXISTS ai_sandbox CASCADE',
		'CREATE SCHEMA ai_sandbox',
	]

	function_strings = create_functions(config)

	grant_statements = [
		f'GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ai_sandbox TO {config.sandbox_db_user}',
	]

	return house_keeping_statements + function_strings + grant_statements

def write_migration_statements(migration_file: Path, migration_statements: list[str]):
	migration_commands = []
	for statement in migration_statements:
		migration_commands.append(
			f"""migrations.RunSQL('''{statement}'''),"""
		)
	migration_string =  '\n'.join(migration_commands)

	with open(migration_file, 'r') as f:
		content = f.read()

	content = content.replace('operations = [', f'operations = [\n{migration_string}')
	
	with open(migration_file, 'w') as f:
		f.write(content)







	
