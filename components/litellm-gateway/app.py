from fastapi import FastAPI

app = FastAPI(title="LiteLLM Gateway Wrapper", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True, "service": "litellm-gateway", "primary_provider": "oci-genai"}

@app.get("/v1/model-policy")
def model_policy():
    return {
        "aliases": ["commandforge-default", "commandforge-fast", "commandforge-reasoning"],
        "credentials": "vault-or-env-reference-only",
        "budget_enforced": True,
    }
