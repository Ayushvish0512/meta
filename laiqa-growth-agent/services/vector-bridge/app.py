"""
Vector Bridge Service
Handles Chroma upserts and retrieval, calls Gemini embeddings API.
n8n calls this service instead of Chroma directly.
"""
import os, hashlib, httpx
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
import chromadb
from chromadb.config import Settings

app = FastAPI(title="Laiqa Vector Bridge")

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

async def verify_key(x_api_key: str = Header(...)):
    if INTERNAL_API_KEY and x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
CHROMA_AUTH_TOKEN = os.getenv("CHROMA_AUTH_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

# Global client and collection cache
chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(
        chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
        chroma_client_auth_credentials=CHROMA_AUTH_TOKEN
    )
)
_collection = None
_http_client = httpx.AsyncClient()

def get_collection():
    global _collection
    if _collection is None:
        _collection = chroma_client.get_or_create_collection(
            name="laiqa_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

async def embed_text(text: str) -> list[float]:
    resp = await _http_client.post(
        f"{GEMINI_EMBED_URL}?key={GEMINI_API_KEY}",
        json={"model": "gemini-embedding-001", "content": {"parts": [{"text": text}]}},
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]

class UpsertRequest(BaseModel):
    doc_id: str
    text: str
    metadata: dict

class QueryRequest(BaseModel):
    query: str
    top_k: int = 10
    where: Optional[dict] = None

class UpsertResponse(BaseModel):
    doc_id: str
    checksum: str

class QueryResponse(BaseModel):
    results: list[dict]

@app.post("/upsert", response_model=UpsertResponse, dependencies=[Depends(verify_key)])
async def upsert(req: UpsertRequest):
    embedding = await embed_text(req.text)
    checksum = hashlib.md5(req.text.encode()).hexdigest()
    collection = get_collection()
    collection.upsert(
        ids=[req.doc_id],
        embeddings=[embedding],
        documents=[req.text],
        metadatas=[{**req.metadata, "checksum": checksum}]
    )
    return UpsertResponse(doc_id=req.doc_id, checksum=checksum)

@app.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_key)])
async def query(req: QueryRequest):
    embedding = await embed_text(req.query)
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return QueryResponse(results=[])
    
    n_results = min(req.top_k, count)
    kwargs = {"query_embeddings": [embedding], "n_results": n_results, "include": ["documents", "metadatas", "distances"]}
    if req.where:
        kwargs["where"] = req.where
    
    results = collection.query(**kwargs)
    docs = []
    if results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            docs.append({
                "text": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
    return QueryResponse(results=docs)

@app.delete("/doc/{doc_id}", dependencies=[Depends(verify_key)])
def delete_doc(doc_id: str):
    get_collection().delete(ids=[doc_id])
    return {"deleted": doc_id}

@app.get("/health")
def health():
    return {"status": "ok", "collection": "laiqa_knowledge"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8002)))
