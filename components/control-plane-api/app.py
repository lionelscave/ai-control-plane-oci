from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI(title="AI Control Plane API", version="0.1.0")

class TaskRequest(BaseModel):
    objective: str
    requested_agent: str | None = None
    workflow: str | None = None
    requires_approval: bool = True

@app.get("/health")
def health():
    return {"ok": True, "service": "control-plane-api", "externalActionExecuted": False}

@app.post("/v1/tasks")
def create_task(task: TaskRequest):
    return {
        "task_id": "local-preview-task",
        "status": "pending_approval" if task.requires_approval else "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "route": task.requested_agent or task.workflow or "agent-router",
    }

@app.get("/v1/architecture")
def architecture():
    return {
        "orchestrator": "LangGraph",
        "model_gateway": "LiteLLM",
        "model_provider": "OCI Generative AI",
        "memory_state": "Oracle AI Database 26ai",
        "tool_gateway": "Oracle MCP Gateway",
        "cache": "OCI Cache Redis/Valkey",
        "ingress": "OCI API Gateway",
    }
