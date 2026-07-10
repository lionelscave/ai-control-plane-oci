# Dev Deployment Plan — AI Control Plane OCI

Status: plan-only until Approval B.

## Deploy order

1. Resource Manager/Terraform validates landing-zone modules.
2. OCIR repositories are created or selected.
3. OKE namespace `ai-control-plane-dev` is prepared.
4. Oracle AI Database 26ai schema migrations are reviewed.
5. OCI Cache Valkey 8.1 endpoint references are configured.
6. LiteLLM, LangGraph, Oracle MCP, control-plane API, and approval gateway containers are built.
7. OCI Functions lightweight actions are packaged.
8. OCI API Gateway routes are configured.
9. No deployment occurs without explicit approval.
