from django.core.management.base import BaseCommand

from rules_tap.embeddings.save_to_store import save_to_store

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        save_to_store()