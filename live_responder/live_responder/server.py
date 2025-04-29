import os
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from typing import List
from live_responder.embeddings.search import search
from live_responder.config import load_config

app = FastAPI()

config = load_config()

class ContextRequest(BaseModel):
    query: str
    k: int = 5

@app.post("/context")
def retrieve_context(request: ContextRequest):
    """
    Retrieve relevant context chunks for a given query using our vector store.
    """
    print("Got request")
    try:
        chunks: List[str] = search(request.query, request.k, config)
        return {"context": chunks}
    except ValueError as e:
        # Missing API key or other client error
        raise HTTPException(status_code=400, detail=str(e))
if __name__ == "__main__":
    import uvicorn  # type: ignore
    # Start the server with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run("live_responder.server:app", host="0.0.0.0", port=8003, reload=True)

