import json
import dataclasses
from typing import Dict, Any
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


from live_responder.embeddings.search import search as fetch_context
from live_responder.sql_gen.transpose import transpose_to_sandbox
from live_responder.config import EmbeddingConfig
from live_responder.logging import logger

PROMPT_TEMPLATE = """
Based on the following database schema documentation, relevant context, and
user query, generate a PostgreSQL 16 SQL query plus a brief explanation.
Return *only* a JSON object that adheres to the schema below—no other text.

Context:
{context}

Schema:
{schema}

{format_instructions}

User Query: {query}
"""


@dataclasses.dataclass
class SQLGenConfig:
	model: str = "gpt-4o-mini"
	temperature: float = 0.0


sql_gen_config = SQLGenConfig()

class SQLResponse(BaseModel):
	sql: str = Field(description="A postgres 16 compliant SQL query")
	explanation: str = Field(description="Explanation of the generated SQL query")


def generate_sql(
	query: str,
	embedding_config: EmbeddingConfig,
	search_k: int = 4,
) -> Dict[str, str]:
	"""Generate a paramete ‑sanitised SQL statement for the given user *query*."""

	logger.info("Fetching %d context documents for: %s", search_k, query)
	context_docs = fetch_context(query, search_k, embedding_config)  # noqa: F821
	context_str = "\n---\n".join(context_docs)

	if not context_docs:
		logger.warning("No context docs found for the query.")

	llm = ChatOpenAI(
		model=sql_gen_config.model,
		temperature=sql_gen_config.temperature,
	)

	parser = PydanticOutputParser(pydantic_object=SQLResponse)

	schema_path = Path(embedding_config.schema_file)
	schema = schema_path.read_text()

	prompt = ChatPromptTemplate.from_template(
		PROMPT_TEMPLATE,
		partial_variables={"format_instructions": parser.get_format_instructions()},
	)

	chain = prompt | llm | parser

	logger.info("Invoking LLM…")
	response: SQLResponse = chain.invoke(
		{
			"context": context_str,
			"schema": schema,
			"query": query,
		}
	)

	# transpose the identifiers if the sandbox uses a different schema name
	logger.info("Response received: \n%s", response.sql)
	logger.info("Transposing generated SQL to sandbox schema…")
	transposed_sql = transpose_to_sandbox(embedding_config, response.sql)  # noqa: F821

	return {"sql": transposed_sql, "explanation": response.explanation}