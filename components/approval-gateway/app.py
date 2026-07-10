from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Approval Gateway", version="0.1.0")

class ApprovalRequest(BaseModel):
    action: str
    risk: str = "medium"
    requested_by: str = "nanoclaw"

@app.get("/health")
def health():
    return {"ok": True, "service": "approval-gateway"}

@app.post("/v1/approvals")
def create_approval(req: ApprovalRequest):
    return {"approval_id": "approval-local-preview", "status": "pending_approval", "action": req.action, "risk": req.risk}
