"""Analyze SQL using Ollama and return structured findings."""
import json
import os

import ollama

from reviewer.prompts import SYSTEM_PROMPT


def analyze_sql(sql_content, filename, model=None):
    """Send SQL to Ollama for analysis and return parsed findings."""
    model = model or os.getenv("OLLAMA_MODEL", "phi3:mini")

    prompt = f"""Review this SQL file: {filename}

```sql
{sql_content}
```

Analyze for performance, security, and best practice issues. Respond in JSON only."""

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            format="json",
        )

        content = response["message"]["content"].strip()
        result = json.loads(content)

        # Validate structure
        if "findings" not in result:
            result = {"findings": [], "summary": "Analysis completed but no structured output."}
        if "summary" not in result:
            result["summary"] = f"Found {len(result['findings'])} issue(s)."

        return result

    except json.JSONDecodeError:
        return {
            "findings": [],
            "summary": f"LLM returned non-JSON response for {filename}. Raw output logged.",
            "raw": content if "content" in dir() else "No response",
        }
    except Exception as e:
        return {
            "findings": [],
            "summary": f"Analysis failed for {filename}: {str(e)}",
            "error": str(e),
        }


def filter_by_severity(findings, min_severity="warning"):
    """Filter findings by minimum severity level."""
    severity_order = {"info": 0, "warning": 1, "error": 2}
    min_level = severity_order.get(min_severity, 0)

    return [
        f for f in findings
        if severity_order.get(f.get("severity", "info"), 0) >= min_level
    ]
