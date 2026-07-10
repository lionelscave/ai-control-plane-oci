from fastapi import FastAPI

app = FastAPI(title="Workflow Workers", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True, "service": "workflow-workers", "orchestrator": "LangGraph"}
