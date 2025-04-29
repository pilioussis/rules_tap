import os
import json
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

def get_context(query: str, k: int = 5) -> List[str]:
	"""
	Retrieves text chunks relevant to a query from a FAISS vector store.

	Args:
		query: The input query string.
		k: The number of relevant chunks to retrieve. Defaults to 5.

	Returns:
		A list of relevant text chunks. Returns an empty list if errors occur
		during loading or retrieval.

	Raises:
		ValueError: If the OPENAI_API_KEY environment variable is not set.
	"""
	# Define paths assuming index was saved to /app/data with name 'vector_index'
	db_folder_path = "./data"
	index_name = "vector_index"

	if not os.getenv("OPENAI_API_KEY"):
		raise ValueError("OPENAI_API_KEY environment variable not set.")

	embeddings = OpenAIEmbeddings()
	# Set allow_dangerous_deserialization=True if the index was saved
	# with custom Python objects. Otherwise, set to False for security.
	# We assume True here for flexibility but review if necessary.

	db = FAISS.load_local(
		folder_path=db_folder_path,
		embeddings=embeddings,
		index_name=index_name,
		allow_dangerous_deserialization=True
	)
	

	retriever = db.as_retriever(search_kwargs={"k": k})
	try:
		relevant_docs = retriever.get_relevant_documents(query)
		return [doc.page_content for doc in relevant_docs]
	except Exception as e:
		print(f"Error retrieving documents: {e}")
		return []

if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is set in your environment
    # Ensure the FAISS index exists at /app/data/vector_index.faiss & .pkl
    test_query = "Example query about the codebase"
    try:
        context_chunks = get_context(test_query, k=3)
        if context_chunks:
            print(f"Found {len(context_chunks)} relevant chunks for '{test_query}':")
            for i, chunk in enumerate(context_chunks):
                print(f"--- Chunk {i+1} ---")
                print(chunk)
        else:
            print(f"No context found or error occurred for query: '{test_query}'")
    except ValueError as e:
        print(e)

	