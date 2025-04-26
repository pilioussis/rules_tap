from django.core.management.base import BaseCommand
from django.conf import settings
from rules_tap.common import load_config
from rules_tap.embeddings.search import search_store

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        config = load_config(settings.RULES_TAP_CONFIG)

        # search_text = input("Enter the text to search: ")
        search_text = "Get me the set of actions where notifications are no longer being sent"
        search_store(config, search_text, n=5)