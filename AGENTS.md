# AGENTS.md -- sql-ops-reviewer

## Project Overview

GitHub Action that reviews `.sql` files in pull requests using a local Ollama
LLM. Posts structured review comments on the PR with severity-tagged findings
for performance, security, and best practice issues. Designed to pair with
`sql-sop` for two-layer SQL quality (static rules + AI review).

## Architecture

```
reviewer/
  main.py              # Entry point: reads env vars, orchestrates pipeline
  diff_parser.py       # Fetches PR changed files via GitHub API, extracts added SQL lines
  sql_analyzer.py      # Sends SQL to Ollama for analysis, parses JSON findings
  prompts.py           # System prompt and review templates
  github_client.py     # Posts PR reviews and fallback comments via GitHub API
action.yml             # Composite GitHub Action definition
requirements.txt       # requests, ollama
tests/
  test_diff_parser.py  # Import smoke tests and severity filter unit tests
```

## Pipeline flow

1. `main.py` reads env vars set by the GitHub Action (`GITHUB_TOKEN`, `REPO`,
   `PR_NUMBER`, `OLLAMA_MODEL`, `MIN_SEVERITY`).
2. `diff_parser.get_changed_sql_files()` calls the GitHub API to get PR file
   diffs, extracts only added lines from `.sql` files.
3. `sql_analyzer.analyze_sql()` sends each SQL file to Ollama with a structured
   system prompt, expects JSON with `findings` and `summary`.
4. `github_client.post_review()` posts a PR review. If the review API fails,
   falls back to `post_comment()` (issue comment).
5. Exit code 1 if any finding has severity `"error"` (blocks merge with
   `REQUEST_CHANGES`).

## Action inputs

- `github-token`: Required. Defaults to `github.token`.
- `model`: Ollama model name. Default: `phi3:mini`.
- `severity`: Minimum severity to report (`info`, `warning`, `error`).
  Default: `warning`.
- `file-pattern`: Glob for SQL files. Default: `**/*.sql`.

## Tests

```bash
python -m pytest tests/ -v
```

## Conventions

- **Structured JSON output**: The LLM is prompted to return only valid JSON.
  `sql_analyzer.py` handles `JSONDecodeError` gracefully and returns a fallback
  result with `"raw"` field.
- **Severity levels**: Three levels -- `info`, `warning`, `error`. The
  `filter_by_severity()` function uses numeric ordering to filter.
- **GitHub API timeouts**: All `requests` calls use `timeout=30`.
- **Fallback pattern**: If the review API call fails, the action posts a plain
  issue comment instead of crashing.
- **No direct dependencies on sql-sop**: This action is independent. They
  complement each other but share no code.

## Environment variables (set by action.yml)

| Variable | Source |
|---|---|
| `GITHUB_TOKEN` | `inputs.github-token` |
| `OLLAMA_MODEL` | `inputs.model` |
| `MIN_SEVERITY` | `inputs.severity` |
| `FILE_PATTERN` | `inputs.file-pattern` |
| `PR_NUMBER` | `github.event.pull_request.number` |
| `REPO` | `github.repository` |
| `HEAD_SHA` | `github.event.pull_request.head.sha` |
| `BASE_SHA` | `github.event.pull_request.base.sha` |
