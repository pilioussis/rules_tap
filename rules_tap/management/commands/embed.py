from django.core.management.base import BaseCommand

from rules_tap.embeddings.save import create_embeddings_and_save_to_db

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        create_embeddings_and_save_to_db()