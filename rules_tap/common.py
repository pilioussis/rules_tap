import hashlib
import shutil
import dataclasses
from typing import Optional, Callable
from pathlib import Path
from django.db import models
from django.db.models import QuerySet
from django.apps import AppConfig
from django.apps import apps
from django.contrib.auth import get_user_model
User = get_user_model()


def get_hash(text: str) -> int:
	hash_obj = hashlib.md5(text.encode('utf-8'))
	hash_bytes = hash_obj.digest()[:8]
	hash_id = int.from_bytes(hash_bytes, byteorder='big', signed=False)
	return hash_id >> 1 # shift right to avoid overflow due to unsigned


@dataclasses.dataclass
class ViewableTable:
	model_class: models.base.ModelBase
	fields: list[str]
	viewable_row_fn: Callable[[User], QuerySet]


@dataclasses.dataclass
class ContextConfig:
	module_names: list[str]
	file_chunk_exclude_paths: list[str]
	table_loader_class_string: str
	open_api_key: str
	work_dir: Path
	migrations_app_label: str
	sandbox_db_user: str

	_migrations_app: Optional[AppConfig] = None
	_viewable_tables: Optional[list[ViewableTable]] = None

	@property
	def chunk_dir(self):
		return self.work_dir / 'chunks'
	
	@property
	def viewable_tables(self):
		if self._viewable_tables:
			return self._viewable_tables
		module_path, var_name = self.table_loader_class_string.rsplit('.', 1)
		module = __import__(module_path, fromlist=[var_name])
		viewable_tables: list[ViewableTable] = getattr(module, var_name)

		assert isinstance(viewable_tables, list)
		assert all(isinstance(table, ViewableTable) for table in viewable_tables)

		self._viewable_tables = viewable_tables
		return viewable_tables
	
	@property
	def migrations_app(self):
		if self._migrations_app:
			return self._migrations_app
		self._migrations_app = apps.get_app_config(self.migrations_app_label)
		return self._migrations_app

	@property
	def code_dir(self):
		return self.chunk_dir / 'code'
	
	@property
	def runtime_dir(self):
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
	return ContextConfig(
		module_names=config['MODULE_PATHS'],
		open_api_key=config['OPENAI_API_KEY'],
		work_dir=Path(config['WORKDIR']),
		file_chunk_exclude_paths=config['FILE_CHUNK_EXCLUDE_PATHS'],
		table_loader_class_string=config['TABLE_LOADER_CLASS_STRING'],
		migrations_app_label=config['MIGRATIONS_APP_LABEL'],
		sandbox_db_user=config['SANDBOX_DB_USER']
	)