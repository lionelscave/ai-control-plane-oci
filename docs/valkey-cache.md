# OCI Cache with Valkey 8.1

OCI Cache with Valkey 8.1 is used for TTL-only acceleration: sessions, idempotency keys, rate counters, distributed locks, and safe response caching. Durable state remains in Oracle AI Database 26ai.

Valkey is not the system of record. It should not store durable memory, approvals, secrets, or unrecoverable workflow state.
