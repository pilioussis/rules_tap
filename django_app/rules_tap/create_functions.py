# -*- coding: utf-8 -*-
import csv, logging, pytz, uuid
from typing import Callable
import time
from django.db import connection
from dataclasses import dataclass
from django.db import models
from decimal import Decimal
from datetime import timedelta, datetime
from colorama import Style, Fore, Back
from django.db.models import QuerySet

from django.db import IntegrityError
from psycopg.errors import UniqueViolation, ExclusionViolation
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch, Case, When, Value
from django.db.models.functions import Extract, TruncMonth, TruncDate, TruncDay, TruncHour, TruncTime
from django.conf import settings
from types import MethodType


from apps.account.models import User
from apps.activity.models import Event
from apps.advice.models import AdviceSubcategory, AdviceCategory, AdviceSection
from apps.answer.models import ANSWER_MODELS, AnswerText, AnswerDate, AnswerDecimal, AnswerBoolean, AnswerFile, InitialAnswer
from apps.answer.query import get_answer_dates_for_notification
from apps.email.models import Email
from apps.file.models import File, Folder
from apps.field.models import Field, TableField, HelpInfo, FieldNotification
from apps.form.models import Form
from apps.form_action.models import FormAction
from apps.form_action.tasks import create_scheduled_actions
from apps.module.models import ModuleTemplate, Module
from apps.organisation.models import Organisation, Team
from apps.pdf.models import PdfGenerator, Pdf
from apps.record.models import Record
from apps.suite.models import Suite
from apps.template.models import FormSet, Template

from apps.answer.serializers import AnswerTextSerializer
from apps.organisation.serializers import TeamSerializer

@dataclass
class Table:
	model: models.base.ModelBase
	rows: Callable[[User], QuerySet]
	fields: list[str]

@dataclass
class Cte:
	name: str
	query_string: str
	columns: list[str]
	def get_token(self, field_name: str) -> str:
		return f"<<{self.name}:{field_name}>>"

TABLES = [
	Table(model=Record, fields=['id', 'name'], rows=Record.objects.viewable),
	Table(model=AnswerText, fields=['id', 'content'], rows=AnswerText.objects.viewable),
]

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

def create_functions():
	stub_user = User(id='<<account_user:id>>', organisation_id='<<account_user:organisation_id>>')

	stub_user.top_level_manager = False
	ctes = [Cte(query_string=str(User.objects.filter(id='global_user_id::int').query), name='account_user', columns=['id', 'organisation_id'])]
	cte_string = ""
	if ctes:
		cte_string = f"""WITH {','.join(
			f"""{c.name} AS ({c.query_string})"""
		for c in ctes)}"""
	
	function_strings = []

	for t in TABLES:
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
