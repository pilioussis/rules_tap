from django.core.management.base import BaseCommand

from rules_tap.embeddings.search import search_store

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        search_store("worker")