# OCI AI Control Plane Landing Zone Design v2

Date: July 9, 2026  
Owner: Lionel Cave / NanoClaw App Factory  
Status: Updated reference architecture draft  
Profile ID: `github-orchestrated-oci-control-plane:v0.4`

## 1. Update Summary

This revision updates the OCI AI Control Plane landing zone to explicitly deploy and govern:

- **LangGraph** for agent/workflow orchestration, durable execution, human-in-the-loop state, and graph runtime
- **LiteLLM** as the model gateway/router/proxy for OCI GenAI and future model providers
- **Oracle MCP** as the controlled tool/data access layer, especially Oracle Database MCP / SQLcl MCP / Database Tools MCP
- **Oracle AI Database 26ai** as the system of record for agent memory, workflow state, vector memory, audit records, and operational state
- **OCI Generative AI** as the default first-party model provider and optional managed agents layer
- **OCI API Gateway** as the governed external API entry point
- **OCI Cache with Valkey / Valkey** for low-latency cache, session acceleration, and transient agent state
- **OCI DevOps + OCIR + Resource Manager/Terraform** as build, artifact, and landing-zone provisioning backbone

## 2. Design Principle

**NanoClaw generates and stages. OCI deploys only after approval.**

The AI control plane should support real deployment later, but generation remains separate from deployment:

1. NanoClaw generates source, Terraform, plans, manifests, and GitHub repo content.
2. Approval A allows repo publish.
3. Approval B allows OCI build/deploy.
4. OCI deployment uses managed services and secret references only.

## 3. Updated High-Level Architecture

```text
User / Operator / External Apps
        |
        v
OCI API Gateway
        |
        v
Control Plane API on OKE
        |
        +--> Auth / Policy / Approval Gateway
        |
        +--> LangGraph Runtime Service
        |       |
        |       +--> Oracle AI Database 26ai
        |       |       - graph checkpoints
        |       |       - workflow state
        |       |       - long-term memory
        |       |       - vector memory
        |       |       - audit records
        |       |
        |       +--> OCI Cache with Valkey 8.1
        |       |       - short TTL cache
        |       |       - session acceleration
        |       |       - rate-limit state
        |       |       - transient graph cache
        |       |
        |       +--> LiteLLM Gateway
        |               |
        |               +--> OCI Generative AI
        |               +--> Optional future providers
        |
        +--> Oracle MCP Gateway
        |       |
        |       +--> Oracle Database MCP / SQLcl MCP / Database Tools MCP
        |       +--> Approved Oracle tools/data sources
        |
        +--> Agent / Workflow Services
                |
                +--> OCI Functions for lightweight actions
                +--> OKE services for long-running workers
```

## 4. Runtime Component Map

| Component | Runtime | Purpose |
|---|---|---|
| `control-plane-api` | OKE | Main API for tasks, sessions, approvals, workflow runs, health, audit |
| `api-gateway` | OCI API Gateway | Governed external HTTPS entry point with auth/rate limiting |
| `approval-gateway` | OKE | Human approval queue and policy enforcement before sensitive actions |
| `langgraph-runtime` | OKE | Runs graphs, agents, checkpointers, state transitions, resumes |
| `litellm-gateway` | OKE | OpenAI-compatible model gateway, routing, budget/rate-limit policy |
| `oracle-mcp-gateway` | OKE | Controlled MCP tool access and Oracle data/tool boundary |
| `memory-state-service` | OKE | Wraps Oracle 26ai memory/state tables and vector search |
| `workflow-workers` | OKE | Long-running graph/workflow execution workers |
| `action-functions` | OCI Functions | Lightweight event-driven agent actions |
| `valkey-cache` | OCI Cache | Low-latency cache and transient state |
| `oracle-26ai` | Oracle AI Database 26ai | Persistent memory, checkpoints, state, vectors, audit |
| `oci-genai-adapter` | OKE service or library | Calls OCI Generative AI through LiteLLM route/provider adapter |

## 5. LangGraph Placement

LangGraph becomes the **agent/workflow orchestration kernel**.

### Responsibilities

- define graph nodes for agents, tools, memory, approval gates, and model calls
- persist execution state after important steps
- resume interrupted/failed workflows
- support human-in-the-loop approval pauses
- expose graph run state to control-plane API
- emit audit events for every graph transition

### LangGraph services

```text
components/langgraph-runtime/
├── graphs/
│   ├── lead-followup.graph.py
│   ├── research-agent.graph.py
│   └── approval-routed-action.graph.py
├── checkpointers/
│   └── oracle26ai_checkpointer.py
├── stores/
│   └── oracle26ai_store.py
├── nodes/
│   ├── model_call.py
│   ├── approval_gate.py
│   ├── memory_retrieve.py
│   ├── mcp_tool_call.py
│   └── audit_emit.py
└── runtime_api.py
```

### State strategy

| State type | Backing service |
|---|---|
| Graph checkpoint | Oracle 26ai relational tables |
| Durable workflow state | Oracle 26ai JSON/document columns or relational tables |
| Long-term memory | Oracle 26ai vector + relational hybrid memory |
| Fast ephemeral state | OCI Cache with Valkey 8.1 |
| Approval wait state | Oracle 26ai + approval gateway |

## 6. LiteLLM Placement

LiteLLM becomes the **model access plane**.

### Responsibilities

- expose OpenAI-compatible model endpoint to LangGraph and agents
- route to OCI Generative AI as primary provider
- provide model aliases instead of hard-coding provider/model in agent code
- enforce budget, rate, fallback, retry, and policy rules
- prepare for future multi-model routing without changing graph code

### Suggested LiteLLM model aliases

```yaml
model_list:
  - model_name: commandforge-default
    litellm_params:
      model: oci_genai/<approved-model-alias>
      api_base: ${OCI_GENAI_ENDPOINT}
      compartment_id: ${OCI_COMPARTMENT_OCID}

  - model_name: commandforge-fast
    litellm_params:
      model: oci_genai/<fast-model-alias>
      api_base: ${OCI_GENAI_ENDPOINT}
      compartment_id: ${OCI_COMPARTMENT_OCID}

  - model_name: commandforge-reasoning
    litellm_params:
      model: oci_genai/<reasoning-model-alias>
      api_base: ${OCI_GENAI_ENDPOINT}
      compartment_id: ${OCI_COMPARTMENT_OCID}
```

Actual model IDs, endpoints, compartment OCIDs, and credentials must come from approved runtime configuration, Vault, or environment references — never from generated source.

## 7. Oracle MCP Placement

Oracle MCP becomes the **controlled tool/data access plane**.

### MCP gateway responsibilities

- run approved MCP servers behind internal network boundaries
- expose only allowlisted MCP tools to LangGraph nodes
- enforce tool policy by agent, workflow, user, and approval state
- log every tool list/read/call result
- block destructive or sensitive database operations unless approved

### Recommended MCP servers / adapters

| MCP component | Purpose |
|---|---|
| Oracle Database Tools MCP | Secure access to Oracle AI Database through Database Tools MCP |
| Oracle SQLcl MCP | Natural-language Oracle DB operations for approved admin/dev flows |
| Oracle DB Documentation MCP | Documentation/reference lookup for generated code and DB usage |
| Custom NanoClaw MCP adapter | Expose approved generated tools and workflow actions |

### MCP policy

Default posture:

```text
Deny by default.
Allow tools by explicit agent/workflow policy.
Require approval for write/delete/admin operations.
Log all tool calls.
No direct public MCP exposure.
```

## 8. Oracle AI Database 26ai Memory and State

Oracle AI Database 26ai becomes the **durable memory, state, and vector intelligence layer**.

### Why Oracle 26ai

Oracle AI Vector Search supports semantic vector search and vector data types/indexes. This makes it suitable for a unified relational + vector memory design where operational state, audit records, and semantic memory can live together.

### Recommended schemas

```sql
AI_CP_WORKFLOW_RUNS
AI_CP_GRAPH_CHECKPOINTS
AI_CP_AGENT_MEMORY
AI_CP_VECTOR_MEMORY
AI_CP_APPROVAL_REQUESTS
AI_CP_TOOL_CALLS
AI_CP_AUDIT_EVENTS
AI_CP_MODEL_CALLS
AI_CP_SESSIONS
AI_CP_CONNECTOR_REGISTRY
```

### Memory table concepts

| Table | Purpose |
|---|---|
| `AI_CP_WORKFLOW_RUNS` | Workflow metadata, status, owners, timestamps |
| `AI_CP_GRAPH_CHECKPOINTS` | Serialized LangGraph checkpoint state |
| `AI_CP_AGENT_MEMORY` | Structured agent/project memory |
| `AI_CP_VECTOR_MEMORY` | Embeddings and semantic memory using vector columns/indexes |
| `AI_CP_APPROVAL_REQUESTS` | Pending/approved/rejected approval states |
| `AI_CP_TOOL_CALLS` | MCP/tool call history |
| `AI_CP_AUDIT_EVENTS` | Immutable audit stream pattern |
| `AI_CP_MODEL_CALLS` | Model routing, cost, latency, token telemetry |
| `AI_CP_SESSIONS` | User/session state and correlation IDs |
| `AI_CP_CONNECTOR_REGISTRY` | Registered connectors and credential references only |

### Memory scopes

```text
project_memory
agent_memory
workflow_memory
user_preferences
business_context
customer_context
approval_history
audit_events
semantic_documents
```

## 9. OCI Generative AI Placement

OCI Generative AI becomes the **default first-party model layer** behind LiteLLM.

### Responsibilities

- provide approved foundation models
- support enterprise governance through OCI IAM and service controls
- optionally use OCI Generative AI Agents for managed agent features where appropriate
- provide embeddings if approved/available for the selected model/region

### Access pattern

```text
LangGraph node -> LiteLLM Gateway -> OCI GenAI adapter -> OCI Generative AI endpoint
```

Do not call OCI GenAI directly from every agent. Route through LiteLLM so model policy, budget, fallback, and logs are centralized.

## 10. OCI API Gateway Placement

OCI API Gateway becomes the **public/private API ingress**.

### Responsibilities

- expose HTTPS endpoints for control-plane API
- route to OKE services or OCI Functions
- enforce authentication and authorization policy
- enable request/response transformations where needed
- enforce rate limiting and CORS policy
- keep internal services private

### Suggested APIs

```text
POST /v1/tasks
GET  /v1/tasks/{id}
POST /v1/workflow-runs
GET  /v1/workflow-runs/{id}
POST /v1/approvals/{id}/approve
POST /v1/approvals/{id}/reject
GET  /v1/audit-events
GET  /v1/health
POST /v1/mcp/tool-call
```

## 11. Valkey / OCI Cache Placement

Use **OCI Cache with Valkey 8.1** for low-latency, non-authoritative runtime acceleration.

### Cache responsibilities

- response cache for safe/repeatable model/tool calls
- session acceleration
- short-lived LangGraph runtime state
- distributed locks for workflow workers
- rate-limit counters
- idempotency keys
- queue hints / backpressure signals

### Do not use Valkey as durable system of record

Durable state belongs in Oracle 26ai. Valkey 8.1 is for speed and TTL state.

### Suggested key patterns

```text
session:{session_id}
workflow:{run_id}:lock
agent:{agent_id}:rate
model:{hash}:cache
approval:{approval_id}:ttl
idempotency:{request_hash}
```

## 12. Updated OCI Compartments

```text
cmp-ai-control-plane
├── cmp-ai-network
├── cmp-ai-security
├── cmp-ai-devops
├── cmp-ai-artifacts
├── cmp-ai-runtime-oke
├── cmp-ai-runtime-functions
├── cmp-ai-api-gateway
├── cmp-ai-database-26ai
├── cmp-ai-cache
├── cmp-ai-genai
├── cmp-ai-observability
└── cmp-ai-data-memory
```

## 13. Updated Network Design

### VCN

`vcn-ai-control-plane` — `10.40.0.0/16`

### Subnets

| Subnet | CIDR | Public? | Purpose |
|---|---:|---|---|
| `snet-api-gateway-public` | `10.40.10.0/24` | Optional public | OCI API Gateway public endpoint |
| `snet-api-gateway-private` | `10.40.11.0/24` | Private | Private API Gateway endpoint |
| `snet-oke-workers-a` | `10.40.20.0/24` | Private | OKE worker nodes |
| `snet-oke-workers-b` | `10.40.21.0/24` | Private | OKE HA workers |
| `snet-functions` | `10.40.25.0/24` | Private | OCI Functions subnet |
| `snet-oracle-26ai` | `10.40.30.0/24` | Private | Oracle AI Database 26ai access |
| `snet-cache` | `10.40.31.0/24` | Private | OCI Cache Valkey 8.1 |
| `snet-devops-private` | `10.40.40.0/24` | Private | private build/deploy access if needed |
| `snet-observability` | `10.40.50.0/24` | Private | logging/monitoring collectors if needed |

## 14. Updated Repository Scaffold

```text
ai-control-plane/
├── README.md
├── handoff.md
├── manifest-index.json
├── components/
│   ├── control-plane-api/
│   ├── approval-gateway/
│   ├── langgraph-runtime/
│   ├── litellm-gateway/
│   ├── oracle-mcp-gateway/
│   ├── memory-state-service/
│   ├── workflow-workers/
│   └── action-functions/
├── oracle-26ai/
│   ├── schema/
│   ├── migrations/
│   ├── vector-indexes/
│   └── seed/
├── oci/
│   ├── buildspec.yaml
│   ├── terraform/
│   │   ├── modules/
│   │   │   ├── network/
│   │   │   ├── iam/
│   │   │   ├── api-gateway/
│   │   │   ├── oke/
│   │   │   ├── functions/
│   │   │   ├── oracle-26ai/
│   │   │   ├── cache/
│   │   │   ├── genai/
│   │   │   ├── devops/
│   │   │   └── observability/
│   │   └── envs/dev/
│   ├── profiles/
│   └── deploy-targets/
├── deploy/
│   ├── dev.plan.md
│   ├── staging.plan.md
│   └── prod.plan.md
└── docs/
    ├── architecture.md
    ├── langgraph-runtime.md
    ├── litellm-gateway.md
    ├── oracle-mcp-gateway.md
    ├── oracle-26ai-memory.md
    ├── api-gateway.md
    ├── valkey-cache.md
    └── approval-boundary.md
```

## 15. Updated OCI DevOps Pipeline

### Plan pipeline

`bp-ai-control-plane-plan`

Steps:

1. validate generated manifest index
2. validate Terraform syntax
3. scan for secrets/OCIDs/tokens
4. validate LangGraph graph definitions
5. validate LiteLLM config has placeholders only
6. validate Oracle MCP tool allowlist
7. validate Oracle 26ai schema migrations
8. produce Resource Manager/Terraform plan
9. produce human-readable deployment plan

### Build pipeline

`bp-ai-control-plane-build-dev`

Steps after approval:

1. build containers:
   - control-plane-api
   - langgraph-runtime
   - litellm-gateway
   - oracle-mcp-gateway
   - approval-gateway
   - memory-state-service
2. package OCI Functions
3. publish images to OCIR dev repos
4. publish build metadata artifact
5. stop before deploy unless deploy approval exists

### Deploy pipeline

`dp-ai-control-plane-dev`

Deploys to:

- OKE namespace: `ai-control-plane-dev`
- OCI Functions application: `ai-control-plane-actions-dev`
- API Gateway deployment: `/v1`
- Oracle 26ai schema migration job
- Valkey 8.1 cache endpoint reference

## 16. Updated Terraform Modules

```text
oci/terraform/modules/
├── compartments
├── iam
├── network
├── api-gateway
├── oke
├── functions
├── oracle-26ai
├── cache-valkey
├── genai
├── devops
├── ocir
├── vault
└── observability
```

### Terraform outputs required by app runtime

```text
API_GATEWAY_ENDPOINT
OKE_CLUSTER_ID
OCIR_REPOSITORY_URLS
ORACLE_26AI_CONNECT_DESCRIPTOR_SECRET_REF
REDIS_ENDPOINT_SECRET_REF
OCI_GENAI_ENDPOINT
OCI_GENAI_COMPARTMENT_REF
LITELLM_MASTER_KEY_SECRET_REF
MCP_TOOL_POLICY_REF
```

All sensitive values must be references, not plaintext.

## 17. Updated Security Controls

### Runtime boundaries

| Boundary | Control |
|---|---|
| Public ingress | API Gateway auth, rate limits, CORS, WAF optional |
| Internal services | private subnets, NSGs, service-to-service auth |
| Model calls | LiteLLM policies, budget/rate controls, logging |
| Tool calls | Oracle MCP allowlist + approval gates |
| Memory writes | Oracle 26ai memory service policy |
| Cache writes | TTL + key namespace + no durable secrets |
| DB credentials | OCI Vault / Resource Manager variables only |

### MCP tool safety

- read-only by default
- write/admin tools disabled unless explicitly approved
- every MCP call tied to workflow run ID and approval state
- tool output filtered before entering model context
- no direct external/public MCP exposure

## 18. Updated Control Plane Data Flow

### Agent run

```text
1. Request enters OCI API Gateway.
2. Control Plane API creates workflow run in Oracle 26ai.
3. LangGraph runtime starts graph with run/session IDs.
4. LangGraph retrieves memory from Oracle 26ai and cache hints from Valkey.
5. LangGraph calls LiteLLM using model alias.
6. LiteLLM routes to OCI GenAI.
7. LangGraph calls Oracle MCP Gateway for approved tools/data.
8. Sensitive action pauses at Approval Gateway.
9. Human approval updates Oracle 26ai state.
10. LangGraph resumes from checkpoint.
11. Audit events and telemetry are written.
```

## 19. Updated Landing Zone Decisions for Lionel

Need decisions before implementation:

1. Use **OKE-first hybrid**? Recommended: yes.
2. Deploy LiteLLM as internal OKE service? Recommended: yes.
3. Use OCI GenAI as the default primary model provider? Recommended: yes.
4. Use Oracle 26ai as authoritative memory/state database? Recommended: yes.
5. Use OCI Cache Valkey 8.1? OCI docs now recommend Valkey 8.1, but Valkey 8.1 is supported. If Lionel specifically wants Valkey, deploy Valkey 8.1; otherwise consider Valkey.
6. Which Oracle MCP mode first?
   - Database Tools MCP managed service
   - SQLcl MCP
   - Oracle DB MCP toolkit container
7. Should Oracle 26ai be Autonomous AI Database, Exadata Database Service, or Base Database Service?
8. Should API Gateway be public, private, or both?

## 20. v0.4 Generator Changes Needed

Update NanoClaw v0.4 to generate:

```text
generated/repo/components/langgraph-runtime/
generated/repo/components/litellm-gateway/
generated/repo/components/oracle-mcp-gateway/
generated/repo/components/memory-state-service/
generated/repo/oracle-26ai/schema/
generated/repo/oracle-26ai/vector-indexes/
generated/repo/oci/terraform/modules/api-gateway/
generated/repo/oci/terraform/modules/cache-valkey/
generated/repo/oci/terraform/modules/oracle-26ai/
generated/repo/oci/terraform/modules/genai/
generated/repo/docs/langgraph-runtime.md
generated/repo/docs/litellm-gateway.md
generated/repo/docs/oracle-mcp-gateway.md
generated/repo/docs/oracle-26ai-memory.md
```

## 21. References

Primary docs consulted:

- LangGraph overview and persistence docs: https://docs.langchain.com/oss/python/langgraph/overview and https://docs.langchain.com/oss/python/langgraph/persistence
- LiteLLM proxy/gateway docs: https://docs.litellm.ai/docs/ and https://docs.litellm.ai/docs/simple_proxy
- Oracle AI Database 26ai AI Vector Search docs: https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/
- Oracle AI Database 26ai AI/ML/Analytics docs: https://docs.oracle.com/en/database/oracle/oracle-database/26/ai.html
- OCI Generative AI docs: https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm
- OCI Generative AI Agents docs: https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/home.htm
- OCI API Gateway docs: https://docs.oracle.com/en-us/iaas/Content/APIGateway/home.htm
- OCI Cache docs: https://docs.oracle.com/en-us/iaas/Content/ocicache/home.htm
- OCI Cache overview and engine versions: https://docs.oracle.com/en-us/iaas/Content/ocicache/overview.htm
- Oracle Database Tools MCP Server docs: https://docs.oracle.com/en-us/iaas/database-tools/doc/working-database-tools-mcp-server.html
- Oracle SQLcl MCP Server docs: https://docs.oracle.com/en/database/oracle/sql-developer-command-line/25.2/sqcug/using-oracle-sqlcl-mcp-server.html
- Oracle MCP repository: https://github.com/oracle/mcp
