from live_responder.config import load_config
from live_responder.embeddings.save import save_embeddings

# Script to save embeddings to a vector store

if __name__ == "__main__":
	config = load_config()
	save_embeddings(config)
