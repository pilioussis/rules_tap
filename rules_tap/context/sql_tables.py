from django.db import connection
from rules_tap.common import ContextConfig


def get_schema_context(config: ContextConfig):
	context = []
	for t in config.viewable_tables:
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
			""", [t.model_class._meta.db_table])
			columns = cursor.fetchall()
			columns_context = []
			for name, type, fk_ref in columns:
				fk_str = f" REFERENCES {fk_ref}" if fk_ref else ""
				columns_context.append(f"  {name} {type}{fk_str}")

			columns_context_string = ",\n".join(columns_context)
			curr = f"CREATE TABLE ai_sandbox.{t.model_class._meta.db_table} (\n{columns_context_string}\n);"
			context.append(curr)
	return context

