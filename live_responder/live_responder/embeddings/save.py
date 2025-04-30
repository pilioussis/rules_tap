import os
from pathlib import Path
from typing import List
from colorama import Fore, Style
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from live_responder.config import EmbeddingConfig
from live_responder.logging import logger


def get_document_chunks(config: EmbeddingConfig) -> List:
	"""Load and chunk documents from the code directory."""
	# Load Python files from data_path
	loader = DirectoryLoader(
		config.code_dir,
		exclude=config.exclude_files,
		glob="**/*.py",
		loader_cls=TextLoader,
		loader_kwargs={"encoding": "utf-8"}
	)
	documents = loader.load()

	# Chunk documents
	splitter = RecursiveCharacterTextSplitter(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
	return splitter.split_documents(documents)


def save_embeddings(config: EmbeddingConfig) -> None:
	"""
	Ingest Python files from config, chunk them, get embeddings and save them to a FAISS index.
	"""
	logger.info("Start saving embeddings")
	if not os.getenv("OPENAI_API_KEY"):
		raise ValueError("OPENAI_API_KEY environment variable not set.")

	chunks = get_document_chunks(config)

	logger.info(f"Total chunks to process: {Fore.GREEN}{len(chunks)}")
	
	embeddings = OpenAIEmbeddings(
		show_progress_bar=True,
		model=config.model,
		# Note: This is different to RecursiveCharacterTextSplitter.chunk_size
		# This sets how many embeddings are sent to the backend at a time
		chunk_size=1000,
	)
	
	vector_store_path = Path(config.work_dir) / (str(config.vector_index_file) + ".faiss")

	if vector_store_path.exists():
		logger.info("Vector database exists, merging new chunks with existing ones")
		# Load existing vector store
		existing_store = FAISS.load_local(
			folder_path=config.work_dir,
			embeddings=embeddings,
			index_name=config.vector_index_file,
			allow_dangerous_deserialization=True
		)
		
		existing_docs = set(doc.page_content for doc in existing_store.docstore._dict.values())
		logger.info(f"Existing docs: {Fore.GREEN}{len(existing_docs)}")
		
		new_chunks = [chunk for chunk in chunks if chunk.page_content not in existing_docs]
		logger.info(f"New chunks: {Fore.GREEN}{len(new_chunks)}")

		if new_chunks:
			new_store = FAISS.from_documents(new_chunks, embeddings)
			existing_store.merge_from(new_store)
			vector_store = existing_store
		else:
			logger.warn(f"{Fore.YELLOW}No new chunks to embed")
			return
	else:
		logger.info("Creating new vector store")
		vector_store = FAISS.from_documents(chunks, embeddings)

	# Not sure if this is needed?
	os.makedirs(config.work_dir, exist_ok=True)

	# Save index locally
	vector_store.save_local(folder_path=config.work_dir, index_name=config.vector_index_file)
	logger.info(f"Saved to {Fore.GREEN}{config.work_dir/config.vector_index_file}")
