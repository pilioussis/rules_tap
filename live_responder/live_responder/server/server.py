import os
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from typing import List
from live_responder.embeddings.search import search
from live_responder.config import load_config
from live_responder.logging import logger
from colorama import Fore

app = FastAPI()

config = load_config()

class ContextRequest(BaseModel):
	query: str
	k: int = 5

@app.post("/context")
def retrieve_context(request: ContextRequest):
	"""Retrieve relevant context chunks for a given query using our vector store."""
	logger.info(f"Got request: {Fore.GREEN}{request}")
	try:
		chunks: List[str] = search(request.query, request.k, config)
		return {"context": chunks}
	except ValueError as e:
		raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
	import uvicorn
	uvicorn.run("live_responder.server:app", host="0.0.0.0", port=8003, reload=True)
