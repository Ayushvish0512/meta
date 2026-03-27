"""
Vector Bridge Service
Handles Chroma upserts and retrieval, calls Gemini embeddings API.
n8n calls this service instead of Chroma directly.
"""
import os, hashlib, httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import chromadb
from chromadb.config import Settings

app = FastAPI(title="Laiqa Vector Bridge")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
CHROMA_AUTH_TOKEN = os.getenv("CHROMA_AUTH_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(
        chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
        chroma_client_auth_credentials=CHROMA_AUTH_TOKEN
    )
)

COLLECTION_NAME = "laiqa_knowledge"

def get_collection():
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

async def embed_text(text: str) -> list[float]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
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

@app.post("/upsert", response_model=UpsertResponse)
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

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    embedding = await embed_text(req.query)
    collection = get_collection()
    kwargs = {"query_embeddings": [embedding], "n_results": req.top_k, "include": ["documents", "metadatas", "distances"]}
    if req.where:
        kwargs["where"] = req.where
    results = collection.query(**kwargs)
    docs = []
    for i, doc in enumerate(results["documents"][0]):
        docs.append({
            "text": doc,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })
    return QueryResponse(results=docs)

@app.delete("/doc/{doc_id}")
def delete_doc(doc_id: str):
    get_collection().delete(ids=[doc_id])
    return {"deleted": doc_id}

@app.get("/health")
def health():
    return {"status": "ok", "collection": COLLECTION_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8002)))
