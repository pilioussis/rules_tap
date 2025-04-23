from django.core.management.base import BaseCommand
from rules_tap.context.main import get_context

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		get_context()