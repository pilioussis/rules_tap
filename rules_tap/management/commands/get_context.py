from django.core.management.base import BaseCommand
from django.conf import settings
from rules_tap.common import load_config
from rules_tap.context.main import get_context

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		config = load_config(settings.RULES_TAP_CONFIG)

		get_context(config)