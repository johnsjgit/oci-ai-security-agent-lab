"""Local, dependency-free policy gate for an OCI AI security copilot reference."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

INJECTION_MARKERS = ("ignore previous instructions", "reveal system prompt", "exfiltrate", "bypass guardrails")
EMAIL_PATTERN = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")


def retrieve(query: str, documents: list[dict[str, Any]]) -> list[str]:
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    ranked = []
    for document in documents:
        text = f"{document.get('title', '')} {document.get('content', '')}".lower()
        score = sum(word in text for word in words)
        if score:
            ranked.append((score, str(document.get("title", "Untitled document"))))
    return [title for _, title in sorted(ranked, reverse=True)[:3]]


def evaluate(query: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = query.lower()
    reasons = []
    if any(marker in normalized for marker in INJECTION_MARKERS):
        reasons.append("possible_prompt_injection")
    if EMAIL_PATTERN.search(query):
        reasons.append("possible_pii")

    request_id = hashlib.sha256(query.encode("utf-8")).hexdigest()[:12]
    if reasons:
        return {"request_id": request_id, "decision": "blocked", "reasons": reasons, "response": "Request blocked by the local policy gate. Review the audit event before retrying.", "human_approval_required": True}

    return {"request_id": request_id, "decision": "allow_with_review", "retrieved_sources": retrieve(query, documents), "response": "Safe local simulation: retrieve approved context, then require human approval before remediation.", "human_approval_required": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Security question to evaluate")
    parser.add_argument("--knowledge-base", type=Path, default=Path("examples/approved-knowledge-base.json"))
    args = parser.parse_args()
    try:
        documents = json.loads(args.knowledge_base.read_text(encoding="utf-8"))["documents"]
    except (OSError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))

    print(json.dumps(evaluate(args.query, documents), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
