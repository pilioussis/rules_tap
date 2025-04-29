import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from live_responder.config import EmbeddingConfig


def get_document_chunks(config: EmbeddingConfig) -> List:
    """Load and chunk documents from the code directory."""
    # Load Python files from data_path
    loader = DirectoryLoader(
        config.code_dir,
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
    Ingest Python files from `data_path`, chunk them, embed them using OpenAIEmbeddings,
    and save the FAISS index to `db_folder_path` with `index_name`. If embeddings already
    exist, only create embeddings for new chunks and merge them with existing ones.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    # Get current chunks
    chunks = get_document_chunks(config)
    print(f"Total chunks to process: {len(chunks)}")
    
    # Initialize embeddings with show_progress_bar=True
    embeddings = OpenAIEmbeddings(show_progress_bar=True)
    
    # Check if embeddings already exist
    vector_store_path = Path(config.work_dir) / (str(config.vector_index_file) + ".faiss")
    print(vector_store_path)
    if vector_store_path.exists():
        print("Vector database exists, merging new chunks with existing ones")
        # Load existing vector store
        existing_store = FAISS.load_local(
            folder_path=config.work_dir,
            embeddings=embeddings,
            index_name=config.vector_index_file,
            allow_dangerous_deserialization=True
        )
        
        # Get existing document contents
        existing_docs = set(doc.page_content for doc in existing_store.docstore._dict.values())
        print("Existing docs: ", len(existing_docs))
        
        # Filter out chunks that already exist
        new_chunks = [chunk for chunk in chunks if chunk.page_content not in existing_docs]
        print("New chunks: ", len(new_chunks))
        if new_chunks:
            # Create embeddings for new chunks with progress bar
            print("Creating embeddings for new chunks...")
            new_store = FAISS.from_documents(new_chunks, embeddings)
            # Merge with existing store
            existing_store.merge_from(new_store)
            vector_store = existing_store
        else:
            print("No new chunks to embed")
            return
    else:
        print("Creating new vector store")
        vector_store = FAISS.from_documents(chunks, embeddings)

    # Ensure the db_folder_path exists
    os.makedirs(config.work_dir, exist_ok=True)

    # Save index locally
    vector_store.save_local(folder_path=config.work_dir, index_name=config.vector_index_file)
    print(f"Saved to {config.work_dir}, {config.vector_index_file}")
