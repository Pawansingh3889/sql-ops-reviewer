"""Post review comments on GitHub pull requests."""
import os
import requests
from reviewer.prompts import REVIEW_HEADER, FINDING_TEMPLATE


SEVERITY_ICONS = {
    "error": ":x:",
    "warning": ":warning:",
    "info": ":information_source:",
}


def post_review(repo, pr_number, token, results, model="phi3:mini"):
    """Post a review comment summarizing all SQL findings."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Build the review body
    body = REVIEW_HEADER.format(model=model)

    total_findings = 0
    has_errors = False

    for file_result in results:
        filename = file_result["filename"]
        analysis = file_result["analysis"]
        findings = analysis.get("findings", [])
        summary = analysis.get("summary", "")

        if not findings:
            body += f"### `{filename}`\n{summary}\n\n"
            continue

        body += f"### `{filename}`\n"
        body += f"*{summary}*\n\n"

        for finding in findings:
            severity = finding.get("severity", "info")
            category = finding.get("category", "general")
            message = finding.get("message", "")
            suggestion = finding.get("suggestion", "")
            icon = SEVERITY_ICONS.get(severity, ":grey_question:")

            if severity == "error":
                has_errors = True

            body += FINDING_TEMPLATE.format(
                icon=icon,
                severity=severity.upper(),
                category=category,
                message=message,
                suggestion=suggestion,
            )
            total_findings += 1

        body += "\n---\n\n"

    # Add footer
    body += f"\n**Total: {total_findings} finding(s) across {len(results)} file(s).**\n"
    body += "\n*Reviewed by [SQL Ops Reviewer](https://github.com/Pawansingh3889/sql-ops-reviewer) using Ollama ({model}).*".format(model=model)

    # Post the review
    event = "REQUEST_CHANGES" if has_errors else "COMMENT"

    review_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    review_data = {
        "body": body,
        "event": event,
    }

    response = requests.post(review_url, headers=headers, json=review_data, timeout=30)

    if response.status_code in (200, 201):
        print(f"Review posted: {total_findings} findings, event={event}")
        return True
    else:
        print(f"Failed to post review: {response.status_code} {response.text}")
        return False


def post_comment(repo, pr_number, token, body):
    """Post a simple comment on a PR (fallback if review API fails)."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    response = requests.post(url, headers=headers, json={"body": body}, timeout=30)

    return response.status_code in (200, 201)
