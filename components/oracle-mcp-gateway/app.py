from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Oracle MCP Gateway", version="0.1.0")
ALLOWLIST = {"oracle26ai.vector_search", "oracle26ai.memory_read", "oracle_docs.search"}

class ToolCall(BaseModel):
    tool: str
    arguments: dict = {}
    approval_id: str | None = None

@app.get("/health")
def health():
    return {"ok": True, "service": "oracle-mcp-gateway", "policy": "deny-by-default"}

@app.get("/v1/tools")
def tools():
    return {"allowlist": sorted(ALLOWLIST)}

@app.post("/v1/tool-call")
def call_tool(call: ToolCall):
    if call.tool not in ALLOWLIST:
        raise HTTPException(status_code=403, detail="Tool blocked by MCP policy")
    return {"tool": call.tool, "status": "approved_for_preview", "result": {"mode": "local-stub"}}
