from typing import Callable
from dataclasses import dataclass
from django.db import models, connection
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from rules_tap.common import ContextConfig

User = get_user_model()


@dataclass
class Cte:
	name: str
	query_string: str
	columns: list[str]
	def get_token(self, field_name: str) -> str:
		return f"<<{self.name}:{field_name}>>"


def get_schema_context():
	context = []
	for t in TABLES:
		with connection.cursor() as cursor:
			cursor.execute("""
				SELECT
					a.attname AS column_name,
					pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
					fk.ref_table
				FROM pg_attribute a
				LEFT JOIN (
				SELECT
					con.conrelid,
					unnest(con.conkey) AS attnum,
					con.confrelid::regclass::text AS ref_table
				FROM pg_constraint con
				WHERE con.contype = 'f'
				) fk ON a.attrelid = fk.conrelid AND a.attnum = fk.attnum
				WHERE a.attrelid = %s::regclass
				AND a.attnum > 0
				AND NOT a.attisdropped
				ORDER BY a.attnum;
			""", [t.model._meta.db_table])
			columns = cursor.fetchall()
			columns_context = []
			for name, type, fk_ref in columns:
				fk_str = f" REFERENCES {fk_ref}" if fk_ref else ""
				columns_context.append(f"  {name} {type}{fk_str}")

			columns_context_string = ",\n".join(columns_context)
			curr = f"CREATE TABLE {t.model._meta.db_table} (\n{columns_context_string}\n);"
			context.append(curr)
	return context

def create_functions(config: ContextConfig):
	stub_user = User(id=1122334455)

	stub_user.top_level_manager = False
	ctes = [Cte(query_string=str(User.objects.filter(id='global_user_id::int').query), name='account_user', columns=['id', 'organisation_id'])]
	cte_string = ""
	if ctes:
		cte_string = f"""WITH {','.join(
			f"""{c.name} AS ({c.query_string})"""
		for c in ctes)}"""
	
	function_strings = []

	for t in config.viewable_tables:
		query_string = cte_string + '\n\n' + str(t.rows(user=stub_user).only(*t.fields).query)

		for cte in ctes:
			for column in cte.columns:
				query_string = query_string.replace(cte.get_token(column), f'(SELECT {column} FROM {cte.name})')

		columns = ', '.join([f'{field_name} {t.model._meta.db_table}.{field_name}%TYPE' for field_name in t.fields])
		function_string = f"""
		CREATE FUNCTION ai_sandbox.{t.model._meta.db_table}(global_user_id TEXT)
		RETURNS TABLE({columns})
		LANGUAGE sql
		STABLE
		SECURITY DEFINER
		AS $$
			{query_string}
		$$;
		"""

		function_strings.append(function_string)
	return function_strings
