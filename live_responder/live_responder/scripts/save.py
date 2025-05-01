from live_responder.config import load_config
from live_responder.embeddings.save import save_embeddings

if __name__ == "__main__":
	config = load_config()
	save_embeddings(config)
