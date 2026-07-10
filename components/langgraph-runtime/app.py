from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LangGraph Runtime", version="0.1.0")

class GraphRun(BaseModel):
    graph: str
    input: dict
    thread_id: str | None = None

@app.get("/health")
def health():
    return {"ok": True, "service": "langgraph-runtime", "state_store": "oracle-26ai", "cache": "redis"}

@app.post("/v1/graph-runs")
def run_graph(run: GraphRun):
    return {
        "run_id": "graph-run-local-preview",
        "graph": run.graph,
        "thread_id": run.thread_id or "thread-local-preview",
        "status": "paused_for_approval",
        "checkpoint_store": "Oracle AI Database 26ai",
    }
