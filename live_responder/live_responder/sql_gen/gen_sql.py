import json
import dataclasses
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


from live_responder.embeddings.search import search as fetch_context
from live_responder.sql_gen.transpose import transpose_to_sandbox
from live_responder.config import EmbeddingConfig, SQLGenConfig
from live_responder.logging import logger

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
	logger.info(f"Fetching {search_k} context documents for query: '{query}'")
	context_docs = fetch_context(query, search_k, embedding_config)
	context_str = "\n---\n".join(context_docs)
	logger.info(f"Fetched {len(context_docs)} context documents.")
	if not context_docs:
		logger.warning("No context documents found for the query.")

	llm = ChatOpenAI(
		model=sql_gen_config.model,
		temperature=sql_gen_config.temperature
	)

	parser = JsonOutputParser(pydantic_object=SQLResponse)

	prompt_template = """
	Based on the following relevant database schema documentation and the user query, generate a PostgreSQL 16 SQL query and a brief explanation for how it answers the query.
	Return the result *only* as a JSON object with keys "sql" and "explanation". Do not include any other text or markdown formatting.

	Context Documentation:
	----------------------
	{context}
	----------------------

	Format Instructions:
	{format_instructions}

	User Query: {query}

	JSON Response:
	"""

	prompt = ChatPromptTemplate.from_template(
		template=prompt_template,
		partial_variables={"format_instructions": parser.get_format_instructions()}
	)

	chain = prompt | llm | parser

	logger.info("Generating SQL with LLM...")
	response: Dict[str, Any] = chain.invoke({"query": query, "context": context_str})
	generated_sql = response.get("sql")
	explanation = response.get("explanation")

	if not generated_sql or not isinstance(generated_sql, str):
			raise ValueError("LLM response missing or invalid 'sql' key.")
	if not explanation or not isinstance(explanation, str):
			raise ValueError("LLM response missing or invalid 'explanation' key.")

	logger.info("Successfully generated SQL and explanation.")
	logger.debug(f"Generated SQL:\n{generated_sql}")
	logger.debug(f"Explanation:\n{explanation}")

	logger.info("Transposing generated SQL...")
	transposed_sql = transpose_to_sandbox(embedding_config, generated_sql)
	logger.debug(f"Transposed SQL:\n{transposed_sql}")

	return {"sql": transposed_sql, "explanation": explanation}