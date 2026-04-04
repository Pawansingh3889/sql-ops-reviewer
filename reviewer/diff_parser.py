"""Extract changed SQL files from a pull request."""
import fnmatch
import os
import requests


def get_changed_sql_files(repo, pr_number, token, file_pattern="**/*.sql"):
    """Fetch files changed in a PR and return SQL file contents."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    sql_files = []
    for file_info in response.json():
        filename = file_info.get("filename", "")

        # Match against pattern (default: **/*.sql)
        if not filename.endswith(".sql"):
            continue

        status = file_info.get("status", "")
        if status == "removed":
            continue

        patch = file_info.get("patch", "")
        if not patch:
            continue

        # Extract added lines from the diff
        added_lines = []
        line_number = 0
        for line in patch.split("\n"):
            if line.startswith("@@"):
                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                parts = line.split("+")[1].split(",")[0] if "+" in line else "1"
                try:
                    line_number = int(parts.split()[0]) - 1
                except (ValueError, IndexError):
                    line_number = 0
                continue
            elif line.startswith("+") and not line.startswith("+++"):
                line_number += 1
                added_lines.append({
                    "content": line[1:],  # Remove the '+' prefix
                    "line": line_number,
                })
            elif line.startswith("-"):
                continue  # Skip removed lines
            else:
                line_number += 1

        if added_lines:
            full_sql = "\n".join(l["content"] for l in added_lines)
            sql_files.append({
                "filename": filename,
                "sql": full_sql,
                "lines": added_lines,
                "patch": patch,
            })

    return sql_files


def get_full_file_content(repo, path, ref, token):
    """Fetch the full content of a file at a specific commit."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.raw",
    }
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.text
    return None
