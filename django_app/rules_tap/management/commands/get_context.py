# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import timedelta, datetime
from django.db import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch, Case, When, Value
from django.db.models.functions import Extract, TruncMonth, TruncDate, TruncDay, TruncHour, TruncTime
from django.conf import settings
from rules_tap.context.main import get_context

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		get_context()