from django.core.management.base import BaseCommand
from django.conf import settings
from rules_tap.common import load_config
from rules_tap.embeddings.save import create_embeddings_and_save_to_db

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        config = load_config(settings.RULES_TAP_CONFIG)

        create_embeddings_and_save_to_db(config)