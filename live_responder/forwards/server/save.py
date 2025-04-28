import os
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def save_code_chunks_to_db(
    data_path: str = "/code/app/data/code",
    db_folder_path: str = "/app/code/data",
    index_name: str = "vector_index",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> None:
    """
    Ingest Python files from `data_path`, chunk them, embed them using OpenAIEmbeddings,
    and save the FAISS index to `db_folder_path` with `index_name`.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    # Load Python files from data_path
    loader = DirectoryLoader(
        data_path,
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
    os.makedirs(db_folder_path, exist_ok=True)

    # Save index locally
    vector_store.save_local(folder_path=db_folder_path, index_name=index_name)
