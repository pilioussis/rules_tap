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


def create_functions(config: ContextConfig):
	field_map = {
		'id': 1122334455,
		'role': '998877',
	}
	stub_user = User(**field_map)
	user_cte_name = 'user_cte'
	user_cte = Cte(query=str(User.objects.filter(id=field_map['id']).only('id', 'role').query), name=user_cte_name)
	cte_string = create_cte([user_cte])
	
	function_strings = []

	for t in config.viewable_tables:
		print(t.model_class._meta.db_table)
		query_string = cte_string + '\n\n' + str(t.viewable_row_fn(stub_user).only(*t.fields).query)
		print(query_string)

		for name, value in field_map.items():
			query_string = query_string.replace(f'{value}', f'(SELECT {name} FROM {user_cte_name})')

		columns = ', '.join([f'{field_name} {t.model_class._meta.db_table}.{field_name}%TYPE' for field_name in t.fields])

		function_string = f"""
		CREATE FUNCTION ai_sandbox.{t.model_class._meta.db_table}(global_user_id TEXT)
		RETURNS TABLE({columns})
		LANGUAGE sql  // This must be sql so to avoid an optimization fence around the function
		STABLE            // These functions will never modify the db
		SECURITY DEFINER  // Allow this function to expose resources the user won't have access to
		AS $$
			{query_string}
		$$;
		"""

		function_strings.append(function_string)
	return function_strings
