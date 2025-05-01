import sys
from colorama import Back, Fore, Style
from live_responder.config import load_config
from live_responder.embeddings.save import save_embeddings
from live_responder.embeddings.search import search
from live_responder.logging import logger


if __name__ == "__main__":
	config = load_config()
	arg = sys.argv[1]
	chunks = search(arg, 3, config)
	
	for i, c in enumerate(chunks):
		logger.info(f"{Back.CYAN}{Fore.BLACK} Chunk {i+1} {Style.RESET_ALL}")
		logger.info(c)

