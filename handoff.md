# OCI AI Control Plane Handoff

## Approval A — GitHub publish

Allows this source scaffold to be created or updated in GitHub. Does not allow OCI build or deployment.

## Approval B — OCI build/deploy

Required before any OCI DevOps build, Resource Manager apply, OCIR publish, OKE deploy, Functions deploy, API Gateway deployment, or Oracle 26ai migration.

## Human reviewer checklist

1. Run `npm run validate`.
2. Review `deploy/dev.plan.md`.
3. Confirm `oci/profiles/github-orchestrated-oci-control-plane.v0.4.json`.
4. Confirm no secrets, OCIDs, PATs, keys, or hard-coded endpoints exist.
5. Confirm Terraform variables are placeholders only.
6. Confirm GitHub Actions are plan-only and do not deploy.
7. Approve OCI deployment separately from GitHub publication.
