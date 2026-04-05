# SQL Ops Reviewer

GitHub Action that auto-reviews .sql files in pull requests using local AI.

No API keys. No cloud. Runs Ollama on the CI runner.

\`\`\`
type    = "GitHub Action"
ai      = "Ollama (local)"
input   = "changed .sql files in PR"
output  = "review comments on the PR"
setup   = "one YAML file"
\`\`\`

---

## What it catches

- SELECT * in production queries
- Missing WHERE on UPDATE/DELETE
- Joins without indexing hints
- Implicit type conversions
- SQL injection patterns

## Setup

Add to .github/workflows/sql-review.yml:

\`\`\`yaml
name: SQL Review
on:
  pull_request:
    paths:
      - "**/*.sql"

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: Pawansingh3889/sql-ops-reviewer@main
\`\`\`

One file. Every PR with SQL changes gets reviewed automatically.

## Why local AI?

Factory compliance databases hold sensitive data. Sending SQL to OpenAI is a compliance risk. Ollama runs on the CI runner. Nothing leaves the machine.
