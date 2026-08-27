# Architecture boundaries

## Trust flow

~~~mermaid
sequenceDiagram
    participant A as Analyst
    participant G as Guardrail service
    participant R as Approved RAG source
    participant M as OCI AI runtime
    participant H as Human approver
    participant C as OCI change path

    A->>G: Security question
    G->>G: Screen prompt injection and PII
    G-->>A: Block and audit when policy fails
    G->>R: Retrieve approved context when allowed
    R->>M: Classified source snippets
    M->>H: Recommendation with citations
    H->>C: Explicitly approved remediation only
~~~

## Deployment controls

| Concern | Recommended control |
| --- | --- |
| Identity | Use workload identity or dynamic groups; avoid long-lived user keys. |
| Secrets | Store sensitive configuration in OCI Vault, never in the repository or prompt. |
| Retrieval | Curate sources, classify them, and enforce ingestion/change review. |
| Guardrails | Screen both input and output for policy issues, prompt injection, and PII. |
| Actions | Keep the agent read-only by default; route changes through a human-approved workflow. |
| Observability | Retain decision metadata and correlation IDs with classification-aware logging. |

## Non-goals

The agent does not autonomously alter cloud resources, issue IAM permissions, or process real customer data. Those boundaries are deliberate: a useful security copilot should improve analyst context without expanding blast radius.
