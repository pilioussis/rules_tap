from django.core.management.base import BaseCommand
from django.conf import settings
from rules_tap.common import load_config
from pydantic import BaseModel
from openai import OpenAI
# from rules_tap.embeddings.common import get_client
# from rules_tap.embeddings.search import search_store
import numpy as np  # type: ignore[import]

class CalendarEvent(BaseModel):
    sql_query: str
    explanation: str

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        MODEL = "o4-mini"
        config = load_config(settings.RULES_TAP_CONFIG)

        # search_text = input("Enter the text to search: ")
        search_text = "Get me the set of actions where notifications are no longer being sent for ANY reason"
        
        search_context = search_store(config, search_text, n=2)
        search_context = "\n\n".join(search_context)

        # Generate SQL query using OpenAI API
        client = get_client(config)
        messages = [
            {"role": "system", "content": "You are a postgres 16 SQL assistant that only outputs the raw SQL query with a separate explanation on what pieces of context you used."},
            {"role": "user", "content": f"Context:\n{search_context}\n\nWrite an SQL for this prompt: {search_text}."}
        ]
        print(f'Asking {MODEL}')
        response = client.beta.chat.completions.parse(
            model=MODEL,
            messages=messages,  # type: ignore[arg-type]
            response_format=CalendarEvent,
        )
        # Ensure content is not None before calling strip
        print(response.choices[0].message.content)
        resp = response.choices[0].message.parsed
        if not resp:
            print("Error: No message content")
            return
        print("Explanation:")
        print(resp.explanation)
        print("SQL:")
        print(resp.sql_query)
