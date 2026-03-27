# Laiqa AI Growth Agent

Multi-agent system for Meta Ads analysis, daily audits, and action proposals.

## Stack
- **n8n** (localhost:5678) — orchestration, scheduling, approvals
- **Gemini API** — generation (gemini-2.0-flash) + embeddings (gemini-embedding-001)
- **Chroma** (localhost:8000) — vector store / RAG memory
- **Postgres** (localhost:5432) — canonical facts, audit logs, approvals
- **Sanitiser service** (localhost:8001) — PII redaction before LLM calls
- **Vector Bridge** (localhost:8002) — Chroma + Gemini embeddings wrapper

## Quick Start

```bash
cp .env.example .env
# Fill in: META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, GEMINI_API_KEY, passwords
bash setup.sh
```

Then import the 5 workflows from `n8n-workflows/` into n8n.

## Agent Roster

| Agent | Workflow | Purpose |
|---|---|---|
| Data Engineer | 01-ingestion | Pulls Meta Insights → Postgres |
| Embedding Refresh | 02-embedding-refresh | Chunks + embeds docs → Chroma |
| Strategy + Optimisation + Compliance | 03-daily-audit | Daily RAG-powered audit → Slack |
| Action Proposal | 04-action-proposal | Queues approved actions |
| Action Execution | 05-action-execution | Executes Meta API writes with hard guards |

## Upload Business Docs

```bash
curl -X POST http://localhost:8002/upsert \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "brand-voice-v1",
    "text": "DOC_TYPE=BRAND_VOICE\n...",
    "metadata": {"doc_type": "BRAND_VOICE", "version": "1"}
  }'
```

## Key Config (in .env)

| Variable | Purpose |
|---|---|
| TARGET_CPA | CPA threshold for scale decisions |
| MAX_DAILY_BUDGET_CHANGE_PCT | Hard cap on budget changes (default 20%) |
| FATIGUE_FREQ_THRESHOLD | Frequency above which creative refresh is flagged |
| MIN_CONVERSIONS_FOR_SCALE | Minimum conversions before scaling |

## Safety Notes

- All Meta writes require human approval via Slack before execution
- Compliance Agent hard-blocks personal attribute and health framing violations
- Free Gemini tier: content may be used to improve Google products — keep prompts to ad data only, never user health profiles
- Gemini spend caps enforced from April 1, 2026 — monitor usage
