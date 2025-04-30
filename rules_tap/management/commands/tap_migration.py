from django.core.management.base import BaseCommand
from django.conf import settings
from rules_tap.common import load_config
from rules_tap.safe_sandbox.create_migration import create_migration
from django.apps import apps

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		config = load_config(settings.RULES_TAP_CONFIG)

		create_migration(config)
