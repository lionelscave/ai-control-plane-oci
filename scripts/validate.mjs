import { readdirSync, readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const required = [
  'components/control-plane-api/app.py',
  'components/langgraph-runtime/app.py',
  'components/litellm-gateway/litellm.config.yaml',
  'components/oracle-mcp-gateway/app.py',
  'oracle-26ai/schema/001_control_plane_tables.sql',
  'oci/buildspec.yaml',
  'oci/terraform/main.tf',
  'oci/profiles/github-orchestrated-oci-control-plane.v0.4.json',
  'handoff.md'
];

const errors = [];
for (const file of required) if (!existsSync(file)) errors.push(`missing ${file}`);

function walk(dir, files = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory() && !['.git', 'node_modules'].includes(entry.name)) walk(path, files);
    else if (entry.isFile()) files.push(path);
  }
  return files;
}

const secretPatterns = [
  /ocid1\.[a-z0-9.-]+/i,
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
  /(?<![A-Z])(?:api[_-]?key|auth[_-]?token|secret[_-]?key|private[_-]?key)\s*[:=]\s*['"][^'"]{8,}/i
];

for (const file of walk('.')) {
  const text = readFileSync(file, 'utf8');
  if (secretPatterns.some((re) => re.test(text))) errors.push(`possible secret in ${file}`);
}

if (errors.length) {
  console.error(JSON.stringify({ ok: false, errors }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ ok: true, checked: required.length, externalActionExecuted: false }, null, 2));
