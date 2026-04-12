"""SQL Ops Reviewer — Main entry point for the GitHub Action."""
import os
import sys

from reviewer.diff_parser import get_changed_sql_files
from reviewer.github_client import post_comment, post_review
from reviewer.sql_analyzer import analyze_sql, filter_by_severity


def main():
    # Read environment variables set by the GitHub Action
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("REPO")
    pr_number = os.environ.get("PR_NUMBER")
    model = os.environ.get("OLLAMA_MODEL", "phi3:mini")
    min_severity = os.environ.get("MIN_SEVERITY", "warning")

    if not all([token, repo, pr_number]):
        print("ERROR: Missing required environment variables (GITHUB_TOKEN, REPO, PR_NUMBER)")
        sys.exit(1)

    print("SQL Ops Reviewer")
    print(f"  Repo: {repo}")
    print(f"  PR: #{pr_number}")
    print(f"  Model: {model}")
    print(f"  Min severity: {min_severity}")
    print()

    # Step 1: Get changed SQL files
    print("Fetching changed SQL files...")
    sql_files = get_changed_sql_files(repo, pr_number, token)

    if not sql_files:
        print("No SQL files changed in this PR. Skipping review.")
        return

    print(f"Found {len(sql_files)} SQL file(s) to review:")
    for f in sql_files:
        print(f"  - {f['filename']} ({len(f['lines'])} changed lines)")
    print()

    # Step 2: Analyze each SQL file
    results = []
    for sql_file in sql_files:
        print(f"Analyzing {sql_file['filename']}...")
        analysis = analyze_sql(
            sql_content=sql_file["sql"],
            filename=sql_file["filename"],
            model=model,
        )

        # Filter by severity
        if "findings" in analysis:
            analysis["findings"] = filter_by_severity(
                analysis["findings"], min_severity
            )

        results.append({
            "filename": sql_file["filename"],
            "analysis": analysis,
        })

        finding_count = len(analysis.get("findings", []))
        print(f"  {finding_count} finding(s): {analysis.get('summary', '')}")

    # Step 3: Post review on the PR
    print()
    print("Posting review...")
    success = post_review(repo, pr_number, token, results, model=model)

    if not success:
        # Fallback: post as a regular comment
        print("Review API failed. Posting as comment...")
        body = "## SQL Ops Reviewer\n\n"
        for r in results:
            body += f"### `{r['filename']}`\n{r['analysis'].get('summary', '')}\n\n"
        post_comment(repo, pr_number, token, body)

    # Summary
    total = sum(len(r["analysis"].get("findings", [])) for r in results)
    errors = sum(
        1 for r in results
        for f in r["analysis"].get("findings", [])
        if f.get("severity") == "error"
    )

    print()
    print(f"Done. {total} finding(s) across {len(results)} file(s).")

    if errors > 0:
        print(f"  {errors} error(s) found — PR review requested changes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
