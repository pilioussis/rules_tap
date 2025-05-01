import shutil
import dataclasses
from typing import Optional, Callable
from pathlib import Path
from django.db import models
from django.db.models import QuerySet
from django.apps import AppConfig
from django.apps import apps
from django.contrib.auth.models import AbstractBaseUser


@dataclasses.dataclass
class ViewableTable:
	""" Represents a table that the sandbox will have access to, with a scoped set of columns"""
	model_class: models.base.ModelBase
	fields: list[str]
	viewable_row_fn: Callable[[AbstractBaseUser], QuerySet]


@dataclasses.dataclass
class ContextConfig:
	""" The config that controls where context is gathered from"""

	module_names: list[str]  # Search paths for files that will be chunked and given to the LLM
	
	file_chunk_exclude_paths: list[str] # glob of exclude paths for the above directories

	viewable_db_tables: str # The restricted set of tables the sandbox will expose

	open_api_key: str

	work_dir: Path # Where context / working files are stored

	migrations_app_label: str # The Django app where the sandbox migrations will be stored

	sandbox_db_user: str # The Postgres db user that will access the sandbox

	_migrations_app: Optional[AppConfig] = None
	_viewable_tables: Optional[list[ViewableTable]] = None

	@property
	def chunk_dir(self):
		return self.work_dir / 'chunks'
	
	@property
	def viewable_tables(self):
		if self._viewable_tables:
			return self._viewable_tables
		module_path, var_name = self.viewable_db_tables.rsplit('.', 1)
		module = __import__(module_path, fromlist=[var_name])
		viewable_tables: list[ViewableTable] = getattr(module, var_name)

		assert isinstance(viewable_tables, list)
		assert all(isinstance(table, ViewableTable) for table in viewable_tables)

		self._viewable_tables = viewable_tables
		return viewable_tables
	
	@property
	def migrations_app(self) -> AppConfig:
		if self._migrations_app:
			return self._migrations_app
		self._migrations_app = apps.get_app_config(self.migrations_app_label)

		if not self._migrations_app:
			raise Exception(f'Django app {self.migrations_app_label} not found')

		return self._migrations_app

	@property
	def code_dir(self):
		return self.chunk_dir / 'code'
	
	@property
	def runtime_dir(self):
		""" Logs will be stored here temporarily, to be aggregated into useful chunks """
		return self.work_dir / 'runtime'
	
	@property
	def sql_log_file(self):
		return self.runtime_dir / 'sql.log'

	@property
	def schema_file(self):
		return self.chunk_dir / 'schema.sql'

	@property
	def stack_trace_log_file(self):
		return self.runtime_dir / 'stack_trace.log'
	
	@property
	def vector_index_file(self):
		return self.work_dir / 'vector_index.faiss'

	@property
	def id_to_text_file(self):
		return self.work_dir / 'id_to_text.json'
	

def rm_dir(dir: Path):
	if dir.exists():
		shutil.rmtree(dir)
	dir.mkdir(parents=True, exist_ok=True)


def load_config(config: dict):
	""" Loads the config from django's settings module"""

	return ContextConfig(
		module_names=config['MODULE_PATHS'],
		open_api_key=config['OPENAI_API_KEY'],
		work_dir=Path(config['WORKDIR']),
		file_chunk_exclude_paths=config['FILE_CHUNK_EXCLUDE_PATHS'],
		viewable_db_tables=config['VIEWABLE_DB_TABLES'],
		migrations_app_label=config['MIGRATIONS_APP_LABEL'],
		sandbox_db_user=config['SANDBOX_DB_USER']
	)