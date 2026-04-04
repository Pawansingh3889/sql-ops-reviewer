<div align="center">

# SQL Ops Reviewer

**AI-powered SQL review for pull requests**

Catches performance anti-patterns, security risks, and optimization opportunities.
Uses Ollama locally — no cloud APIs, no data leaves your CI runner.

[![GitHub Action](https://img.shields.io/badge/GitHub_Action-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/marketplace/actions/sql-ops-reviewer)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-000000?style=for-the-badge)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)]()

</div>

---

## What It Does

When a developer opens a pull request that modifies `.sql` files, SQL Ops Reviewer:

1. Extracts the changed SQL from the PR diff
2. Sends it to a local Ollama model (phi3:mini by default)
3. Analyzes for **10 categories** of issues
4. Posts a structured review comment directly on the PR

No API keys. No cloud. No data leaves your GitHub Actions runner.

## What It Catches

| Category | Examples |
|---|---|
| **Performance** | `SELECT *`, missing `WHERE` clause, subqueries that should be JOINs, functions on indexed columns, missing `LIMIT`/`TOP` |
| **Security** | SQL injection via string concatenation, hardcoded credentials, dynamic SQL without parameterization |
| **Best Practices** | Missing table aliases, inconsistent naming, no transaction handling, deprecated syntax |

## Quick Start

Add this to your repository:

```yaml
# .github/workflows/sql-review.yml
name: SQL Review
on:
  pull_request:
    paths:
      - '**/*.sql'

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Pawansingh3889/sql-ops-reviewer@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

That's it. Every PR that touches a `.sql` file will get an automated review.

## Configuration

| Input | Default | Description |
|---|---|---|
| `github-token` | `${{ github.token }}` | GitHub token for posting reviews |
| `model` | `phi3:mini` | Ollama model to use |
| `severity` | `warning` | Minimum severity to report (`info`, `warning`, `error`) |
| `file-pattern` | `**/*.sql` | Glob pattern for SQL files |

### Example: Stricter reviews with a larger model

```yaml
- uses: Pawansingh3889/sql-ops-reviewer@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    model: 'llama3.1:8b'
    severity: 'error'
```

## How It Works

```
PR opened with .sql changes
         |
         v
+------------------+
| GitHub Actions   |
| runner (Ubuntu)  |
|                  |
| 1. Install Ollama|
| 2. Pull model    |
| 3. Parse PR diff |
| 4. Analyze SQL   |
| 5. Post review   |
+------------------+
         |
         v
Review comment on PR
with findings + suggestions
```

The action runs entirely inside the GitHub Actions runner. Ollama is installed at runtime, the model is pulled (cached after first run), and the SQL is analyzed locally. Nothing leaves the runner.

## Review Output

The action posts a review comment like this:

> ## SQL Ops Reviewer
>
> ### `migrations/001_create_orders.sql`
> *Found 2 issue(s).*
>
> :warning: **WARNING** (performance): Query uses SELECT * which fetches all columns including BLOBs
> > Replace with specific columns: SELECT order_id, customer_id, total_amount FROM orders
>
> :x: **ERROR** (security): String concatenation in WHERE clause creates SQL injection risk
> > Use parameterized queries: WHERE customer_id = @customer_id
>
> **Total: 2 finding(s) across 1 file(s).**

If any **error**-level findings are detected, the action requests changes on the PR.

## Requirements

- GitHub Actions runner with at least 7GB RAM (standard `ubuntu-latest` works)
- SQL files in the repository (`.sql` extension)
- No API keys or cloud accounts needed

## Performance

| Model | RAM Usage | Review Time (per file) | Accuracy |
|---|---|---|---|
| phi3:mini (default) | ~4 GB | 10-20 seconds | Good for common patterns |
| llama3.1:8b | ~6 GB | 20-40 seconds | Better for complex queries |

First run takes longer due to model download (~2.5 GB for phi3:mini). Subsequent runs use the cached model.

## Project Structure

```
sql-ops-reviewer/
├── action.yml              # GitHub Action metadata
├── reviewer/
│   ├── main.py             # Entry point
│   ├── diff_parser.py      # Extract SQL from PR diffs
│   ├── sql_analyzer.py     # Ollama SQL analysis
│   ├── github_client.py    # Post PR review comments
│   └── prompts.py          # Analysis prompts
├── tests/
│   └── test_diff_parser.py # Unit tests
├── requirements.txt
├── LICENSE
└── README.md
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome.

## License

MIT

---

<div align="center">

**Built by [Pawan Singh Kapkoti](https://pawansingh3889.github.io)**

[![Hire Me](https://img.shields.io/badge/Hire_Me-22c55e?style=for-the-badge)](mailto:pawankapkoti3889@gmail.com) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/pawan-singh-kapkoti-100176347) [![GitHub](https://img.shields.io/badge/GitHub-0f172a?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Pawansingh3889)

</div>
