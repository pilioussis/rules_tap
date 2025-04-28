from fastapi import FastAPI, HTTPException
from typing import List
from search import get_context

app = FastAPI()

@app.get("/context")
def retrieve_context(query: str, k: int = 5):
    """
    Retrieve relevant context chunks for a given query using our vector store.
    """
    print("Got request")
    try:
        chunks: List[str] = get_context(query, k)
        return {"context": chunks}
    except ValueError as e:
        # Missing API key or other client error
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn  # type: ignore
    # Start the server with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)

