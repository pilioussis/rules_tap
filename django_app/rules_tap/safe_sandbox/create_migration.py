# -*- coding: utf-8 -*-
import csv, logging, pytz, uuid, os
import time
from dataclasses import dataclass
from django.core.management import call_command
from django.db import models
from decimal import Decimal
from datetime import timedelta, datetime
from colorama import Style, Fore, Back
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
from .create_functions import create_functions

DB_USER = 'mr_ai'

def create_migration():
	function_strings = create_functions()

	call_command('makemigrations', 'internal', empty=True, name="sandbox_ai")

	directory = os.path.join(settings.BASE_DIR, '..', 'apps', 'internal', 'migrations')

	files = os.listdir(directory)
	files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
	files.sort()
	print(files)
	last_file = files[-2] if files else None
	if not last_file:
		raise Exception('No migrations found')

	qualified_last_file_path = os.path.join(directory, last_file)
	print(qualified_last_file_path)
	with open(qualified_last_file_path, 'r') as f:
		content = f.read()
	print(content)

	house_keeping_statements = [
		'DROP SCHEMA IF EXISTS ai_sandbox CASCADE',
		'CREATE SCHEMA ai_sandbox',
	]

	grant_statements = [
		f'GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ai_sandbox TO {DB_USER}',
	]

	statements = house_keeping_statements + function_strings + grant_statements

	migration_commands = []
	for statement in statements:
		migration_commands.append(
			f"""migrations.RunSQL('''{statement}'''),"""
		)
	migration_string =  '\n'.join(migration_commands)

	content = content.replace('operations = [', f'operations = [\n{migration_string}')

	print(content)
	
	with open(qualified_last_file_path, 'w') as f:
		f.write(content)




	
