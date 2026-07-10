from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Memory State Service", version="0.1.0")

class MemoryQuery(BaseModel):
    scope: str
    query: str

@app.get("/health")
def health():
    return {"ok": True, "service": "memory-state-service", "database": "Oracle AI Database 26ai"}

@app.post("/v1/memory/search")
def search_memory(q: MemoryQuery):
    return {"scope": q.scope, "matches": [], "backend": "oracle-26ai-vector-search", "mode": "local-stub"}
