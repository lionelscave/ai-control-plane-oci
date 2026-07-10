-- Oracle AI Database 26ai schema for AI Control Plane memory and state.
-- Placeholder DDL; review before applying through approved migration.

CREATE TABLE ai_cp_workflow_runs (
  run_id VARCHAR2(128) PRIMARY KEY,
  workflow_name VARCHAR2(255),
  status VARCHAR2(64),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE ai_cp_graph_checkpoints (
  checkpoint_id VARCHAR2(128) PRIMARY KEY,
  run_id VARCHAR2(128),
  thread_id VARCHAR2(128),
  checkpoint_json CLOB CHECK (checkpoint_json IS JSON),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_cp_agent_memory (
  memory_id VARCHAR2(128) PRIMARY KEY,
  scope VARCHAR2(128),
  content CLOB,
  metadata_json CLOB CHECK (metadata_json IS JSON),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_cp_approval_requests (
  approval_id VARCHAR2(128) PRIMARY KEY,
  status VARCHAR2(64),
  action_summary VARCHAR2(1000),
  request_json CLOB CHECK (request_json IS JSON),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_cp_audit_events (
  event_id VARCHAR2(128) PRIMARY KEY,
  run_id VARCHAR2(128),
  event_type VARCHAR2(128),
  event_json CLOB CHECK (event_json IS JSON),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
