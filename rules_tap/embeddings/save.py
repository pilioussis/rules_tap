import os
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from rules_tap.common import Config


def save_chunks_to_db(config: Config) -> None:
    """
    Ingest Python files from `data_path`, chunk them, embed them using OpenAIEmbeddings,
    and save the FAISS index to `db_folder_path` with `index_name`.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    # Load Python files from data_path
    loader = DirectoryLoader(
        config.code_dir,
        glob="**/*.py",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()

    # Chunk documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)

    # Initialize embeddings and create FAISS vector store
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)

    # Ensure the db_folder_path exists
    os.makedirs(config.work_dir, exist_ok=True)

    # Save index locally
    vector_store.save_local(folder_path=config.work_dir, index_name=config.index_name)
    print("saved to ",config.work_dir, config.index_name)
