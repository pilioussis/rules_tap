from django.core.management.base import BaseCommand
from django.conf import settings
from rules_tap.common import load_config
from rules_tap.embeddings.search import search_store

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        config = load_config(settings.RULES_TAP_CONFIG)

        search_store(config, "example text")