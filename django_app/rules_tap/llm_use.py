from django.conf import settings
from .create_functions import get_schema_context
import os
from openai import OpenAI

def get_instructions():
	schema_context = get_schema_context()

	return f"""
		You are an SQL expert. You will be given a prompt and you will generate a correct SQL that satisfies the prompt. 

		We have have a postgres 16 database. Write queries to be used by Metabase v54. Use the schema above to write a query that can be used in Metabase. Use CTEs where appropriate.

		Business teminology:
		- The important table is the answer_answertext table, this stores information that applies to both field_field and field_tablefield
		- The field_field table can be a table, if it is, the answer will also have the table_field_id set.
		- If field_field.type is TABLE, the type of each answer will be specified by the field_tablefield.type. If the field_field.type is not TABLE, the type of each answer will be specified by the field_field.type.
		- Answers have an object_id, which can map to a record_record, organisation_team, or organisation_organisation. Always filter results so that are record_record by filtering answer_answertext.content_type_id = 8.
		- Form actions (represented by the form_action_formaction table) help create workflows for people to complete forms at certain times. They can be created on a schedule (represented by form_action_formactionschedule) or by themselves. If a form action hasn't been completed and form_action_formactionescalation exists, a form_action_formactionescalationevent will be created.
		- Records (record_record) belong to a team (organisation_team). Each record has forms that contains fields with answers.
		- Users generate pdfs either through an action, or directly and generate a pdf_pdf

		Often id and datetime fields are nullable to indicate that an object may be deleted (deactivated) or doens't have that relationship.

		Any integer id variables that are passed in to metabase should be cast to an integer, and UUID id fields should be cast to a UUID.
		{'\n'.join(schema_context)}
		Only output the SQL, nothing else.
	"""


client = OpenAI(
    # This is the default and can be omitted
    api_key=settings.OPENAI_API_KEY,
)

def generate_sql_with_llm(prompt):
	instructions = get_instructions()

	response = client.responses.create(
		model="gpt-4o",
		instructions=instructions,
		input=prompt,
	)
	print(response)
	sql = response.output[0].content[0].text

	return sql, True