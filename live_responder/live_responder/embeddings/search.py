import os
from typing import List
from colorama import Fore, Back, Style
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


from live_responder.config import EmbeddingConfig
from live_responder.logging import logger


def search(query: str, k: int, config: EmbeddingConfig) -> List[str]:
	logger.info(f"Searching for {query}")
	if not os.getenv("OPENAI_API_KEY"):
		raise ValueError("OPENAI_API_KEY environment variable not set.")

	embeddings = OpenAIEmbeddings(
		show_progress_bar=True,
		model=config.model,
	)

	db = FAISS.load_local(
		folder_path=str(config.work_dir),
		embeddings=embeddings,
		index_name=str(config.vector_index_file),
		allow_dangerous_deserialization=True,
	)

	retriever = db.as_retriever(search_kwargs={"k": k})

	# use the new invoke method instead of the deprecated get_relevant_documents
	relevant_docs = retriever.invoke(query)  # returns List[Document] :contentReference[oaicite:0]{index=0}
	doc_strings = [doc.page_content for doc in relevant_docs]

	for i, doc in enumerate(doc_strings):
		logger.info(f"{Back.CYAN}{Fore.BLACK} Context Chunk {i + 1} {Style.RESET_ALL}\n{doc}\n")
	return doc_strings