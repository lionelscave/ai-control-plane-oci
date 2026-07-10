-- Oracle 26ai vector memory placeholder.
-- Review dimensions/model before applying.

CREATE TABLE ai_cp_vector_memory (
  memory_id VARCHAR2(128) PRIMARY KEY,
  scope VARCHAR2(128),
  content CLOB,
  embedding VECTOR,
  metadata_json CLOB CHECK (metadata_json IS JSON),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example only; choose index type/options after sizing and model decision.
-- CREATE VECTOR INDEX ai_cp_vector_memory_idx ON ai_cp_vector_memory (embedding);
