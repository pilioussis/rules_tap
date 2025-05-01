from dataclasses import dataclass
from django.db import models, connection
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from rules_tap.common import ContextConfig, ViewableTable
from django.contrib.auth.models import AbstractUser
User = get_user_model()


# The function param name used in every function
AUTHENTICATED_USER_ID_VARIABLE = 'authenticated_user_id'
USER_CTE_NAME = 'user_cte'


@dataclass
class Cte:
	name: str
	query: str


def create_functions(config: ContextConfig) -> list[str]:
	"""Generate a list of create function statements that will expose config.viewable_tables"""
	
	# TODO: Move this to config
	user_field_map = {
		'id': 1122334455,
		'role': '998877',
	}
	stub_user = User(**user_field_map)
	
	cte_string = create_user_cte(stub_user)
	
	function_strings = []

	for t in config.viewable_tables:
		function_string = create_function(
			table=t,
			user_field_map=user_field_map,
			cte_string=cte_string,
			stub_user=stub_user,
		)
		function_strings.append(function_string)

	return function_strings


def create_function(*, table: ViewableTable, user_field_map: dict, cte_string: str, stub_user: AbstractUser):
	query_string = get_sql_string(table.viewable_row_fn(stub_user).only(*table.fields))

	for name, value in user_field_map.items():
		query_string = query_string.replace(f'{value}', f'(SELECT {name} FROM {USER_CTE_NAME})')

	query_string = cte_string + '\n\n' + query_string

	columns = ', '.join([f'{field_name} {table.model_class._meta.db_table}.{field_name}%TYPE' for field_name in table.fields])

	function_string = '\n        '.join([
		f"CREATE FUNCTION ai_sandbox.{table.model_class._meta.db_table}({AUTHENTICATED_USER_ID_VARIABLE} INTEGER)",
		f"RETURNS TABLE({columns})",
		f"LANGUAGE sql ",  # This must be sql so to avoid an optimization fence around the function
		f"STABLE ",  # These functions will never modify the db
		f"SECURITY DEFINER ",  # Allow this function to expose resources the user won't have access to
		f"AS $$",
		f"	{query_string}",
		f"$$;",
	])
	return function_string


def create_user_cte(stub_user: AbstractUser):
	""" Get the CTE which will expose the user to every function body """
	user_cte_string = get_sql_string(User.objects.filter(id=stub_user.id).only('id', 'role'))
	# Replace the stub id, with the param passed to the function
	user_cte_string = user_cte_string.replace(str(stub_user.id), AUTHENTICATED_USER_ID_VARIABLE)
	
	user_cte = Cte(query=user_cte_string, name=USER_CTE_NAME)
	return create_cte_string([user_cte])


def create_cte_string(ctes: list[Cte]):
	return f"""WITH {','.join(
		f"""{c.name} AS ({c.query})"""
	for c in ctes)}"""


def get_sql_string(qs: QuerySet):
	"""Format a query with params in place, exactly as they will be handed to the db"""
	sql, params = qs.query.sql_with_params()
	with connection.cursor() as cur:
		full_sql = cur.mogrify(sql, params).decode()
	return full_sql

