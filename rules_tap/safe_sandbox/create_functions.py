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
	query: str

def create_cte(ctes: list[Cte]):
	if not ctes:
		raise Exception("No CTEs provided")

	cte_string = f"""WITH {','.join(
		f"""{c.name} AS ({c.query})"""
	for c in ctes)}"""
	return cte_string

def get_sql_string(qs: QuerySet):
	sql, params = qs.query.sql_with_params()    # keeps the %s placeholders
	with connection.cursor() as cur:
		full_sql = cur.mogrify(sql, params).decode()  # psycopg2/3
	return full_sql


def create_functions(config: ContextConfig):
	USER_ID_VARIABLE = 'global_user_id'
	field_map = {
		'id': 1122334455,
		'role': '998877',
	}
	stub_user = User(**field_map)
	user_cte_name = 'user_cte'
	cte_string = get_sql_string(User.objects.filter(id=field_map['id']).only('id', 'role'))
	cte_string = cte_string.replace(str(field_map['id']), USER_ID_VARIABLE)
	user_cte = Cte(query=cte_string, name=user_cte_name)
	cte_string = create_cte([user_cte])
	
	function_strings = []

	for t in config.viewable_tables:
		query_string = get_sql_string(t.viewable_row_fn(stub_user).only(*t.fields))

		for name, value in field_map.items():
			query_string = query_string.replace(f'{value}', f'(SELECT {name} FROM {user_cte_name})')

		query_string = cte_string + '\n\n' + query_string

		columns = ', '.join([f'{field_name} {t.model_class._meta.db_table}.{field_name}%TYPE' for field_name in t.fields])

		function_string = '\n        '.join([
		f"CREATE FUNCTION ai_sandbox.{t.model_class._meta.db_table}({USER_ID_VARIABLE} INTEGER)",
		f"RETURNS TABLE({columns})",
		f"LANGUAGE sql ",  # This must be sql so to avoid an optimization fence around the function
		f"STABLE ",  # These functions will never modify the db
		f"SECURITY DEFINER ",  # Allow this function to expose resources the user won't have access to
		f"AS $$",
		f"	{query_string}",
		f"$$;",
		])

		function_strings.append(function_string)
	return function_strings


