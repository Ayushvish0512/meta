Flow "meta agent\laiqa_pipeline_health_audit.svg"

🧩 System Understanding
The system is a multi-agent marketing automation stack for Laiqa Wellness. The intended pipeline: Meta Ads data → Postgres → Chroma (via Vector Bridge) → RAG-powered multi-agent audit (Strategy + Optimisation + Compliance + Copywriting) → Slack approval → Meta API writes. Supporting services include a Presidio-based PII sanitiser and a Gemini embedding wrapper. Orchestrated via n8n with Gemini for generation.
The architecture concept is solid. The implementation has critical bugs that would prevent the system from running at all in its current state, not just reducing quality.

❌ Critical Issues (must fix)
1. WF01 — Parallel branch has no Merge node (system will silently produce wrong data)
The Schedule Trigger fans out to 3 parallel HTTP nodes (Campaign, AdSet, Ad insights), which all connect to "Normalise + Validate". In n8n, without a Merge node, each branch triggers the Code node independently — once per branch. So the Code node runs 3 times, each time only seeing data from its own triggering branch.
The code does this:
jsconst campaigns = $('Fetch Campaign Insights').item.json.data || [];
const adsets = $('Fetch AdSet Insights').item.json.data || [];
When triggered from the Ad branch, $('Fetch Campaign Insights') returns null → allRows is built from only ad data → the upsert sends 1/3 of the data, 3 times, with each run thinking it's processing everything.
Fix: Add an n8n Merge node (mode: Merge by Index or Append) between the 3 HTTP nodes and the Code node. The Code node then runs once with all 3 branches merged.

2. WF03 — Compliance Agent gets zero data (the audit's most critical gate is a no-op)
The Compliance Agent node's prompt contains {{$json.copy_variants}}. There is no Copywriting Agent anywhere in WF03's node list or connections. Nothing generates copy_variants. This means:

$json.copy_variants is undefined/empty
The Compliance Agent reviews nothing
It returns a PASS verdict on an empty input every single time
WF04 gates on this PASS — so the whole compliance gate is broken

Fix: Add a Copywriting Agent node (using copywriting-agent.txt prompt) before the Compliance Agent. Wire its output as the input to the Compliance Agent.

3. WF03 — Strategy Agent triggered twice without a Merge, gets only half its context
The Strategy Agent is connected from two upstream nodes: "Fetch 7-Day KPI Snapshot" AND "Retrieve Fatigue Context". Without a Merge node, n8n triggers the Strategy Agent twice — once with KPI data only, once with RAG context only. The final report is assembled from whichever execution ran last.
Fix: Add a Merge node that combines both outputs, then feed the merged result into the Strategy Agent.

4. WF04 — plan_id is never generated
The SQL insert uses '{{$json.plan_id}}' and the Slack message references it too. But plan_id is not generated anywhere in this workflow. It presumably comes from WF03's output, but WF04 is a standalone webhook-triggered workflow with no guaranteed input schema from WF03.
Fix: Generate plan_id at the start of WF04 using a Code node: const plan_id = 'plan_' + Date.now() + '_' + Math.random().toString(36).slice(2,7). Store it in the workflow data and reference it consistently.

5. WF04 — No webhook to capture Slack approval response (the approval loop is broken)
WF04 sends a Slack interactive message with Approve/Reject buttons. But there is no Webhook node to receive Slack's callback when a button is clicked. The PRD mentions a "Wait" node for webhook callback capture — it doesn't exist. Without this, approvals can never reach WF05.
Fix: Add a Webhook node (e.g., webhookId: "slack-approval-callback") as the bridge. Slack's interactive payloads need to be sent to this URL. Then parse payload.actions[0].value to get APPROVED/REJECTED and look up the plan by plan_id from payload.message.blocks.

6. WF05 — $json.response doesn't exist; Log Execution will always write null
In the "Log Execution" node:
sqlmeta_api_response = '{{JSON.stringify($json.response)}}'::jsonb
$json.response is not a field on the current item. The actual Meta API response from the previous node would be accessed as $('Execute Meta API Call').item.json. This silently inserts null into the audit log — destroying your ability to track what actually happened or roll back.
Fix: Change to $('Execute Meta API Call').item.json and test the JSON serialization.

7. SQL injection across every single Postgres node
Every workflow uses template literals in raw SQL:
sqlWHERE plan_id = '{{$json.plan_id}}'
VALUES ('{{$json.raw_json}}'::jsonb)
If any entity_id, plan_id, or JSON field contains a single quote or SQL metacharacter, this breaks the query or allows injection. n8n's Postgres node supports named parameters — use them.
Fix: Switch to parameterized queries using n8n's $json binding syntax or the "Query Parameters" field in the Postgres node, which safely escapes values:
sqlINSERT INTO meta_insights_daily (date, entity_level, entity_id, spend)
VALUES ($1, $2, $3, $4)

8. Marketing instruction doc directly conflicts with the Compliance Agent (fundamental business logic clash)
The marketing playbook (# 🔥 4. Script Creation Framework) explicitly lists these as good hooks:

"If you have PCOS, stop doing this immediately" — audience segment targeting
"This symptom means your hormones are crashing" — fear/negative framing
"Are your hormones making you gain weight?" — implied personal attribute

The Compliance Agent hard-fails every single one of these patterns:

"Personal attribute assertions: 'Do you have PCOS?', 'Are you pregnant?', 'Struggling with hormones?'"
"Negative self-perception: body shame, fear-based health framing"

The system is architecturally set up to reject its own marketing team's entire creative strategy. This isn't a bug — it's a contradiction between two documents that both claim to be authoritative. Someone needs to decide: is "If you have PCOS" acceptable or not? Because right now both answers are simultaneously in production.

9. Gemini spend caps start April 1, 2026 — that is 5 days away
The research doc explicitly notes this. From today (March 27, 2026), you have 5 days before Google starts enforcing spend caps on the Gemini free tier. If the system runs at scale (500 performance cards embedded daily + 4 agent calls per audit), it will hit limits immediately. You need to either:

Move to a paid Gemini plan now, or
Implement aggressive token budgeting and batching before April 1


10. No authentication on microservices (both ports exposed with zero auth)
The Sanitiser (8001) and Vector Bridge (8002) have no API key, no bearer token, no IP allowlist — nothing. Port 8001 can be used to probe/redact arbitrary text. Port 8002 allows anyone to inject documents into your Chroma knowledge base (/upsert) or query all embedded data (/query) or delete any document (/delete/{doc_id}). This is a complete knowledge base poisoning risk.
Fix: Add an X-API-Key header check as FastAPI middleware:
pythonfrom fastapi import Header, HTTPException
async def verify_key(x_api_key: str = Header(...)): 
    if x_api_key != os.getenv("INTERNAL_API_KEY"):
        raise HTTPException(status_code=403)

⚠️ Important Improvements
WF02 calls the wrong sanitiser. Despite having a fully built Presidio-based Sanitiser service (with NER models for names, locations, medical info), WF02 uses a basic 2-line regex in a Code node. The /sanitise endpoint on port 8001 is never called from any workflow. Either wire WF02 to call http://sanitiser:8001/sanitise per document, or the Sanitiser service is dead weight.
Vector Bridge creates a new httpx.AsyncClient() per request. embed_text opens and closes a TCP connection for every single embedding call. With 500 documents in WF02, that's 500 TCP handshakes to Google's API. Use a module-level persistent client:
python_http = httpx.AsyncClient()
async def embed_text(text): 
    resp = await _http.post(...)
get_collection() is called on every Chroma request. This issues a network call to Chroma to look up or create the collection on every /upsert and /query. Cache it at startup: _collection = get_collection() and reference _collection directly.
Chroma will throw if n_results > collection size. WF03 queries with top_k=8. If the collection has fewer than 8 documents (e.g., on first run), Chroma raises an exception and kills the audit. Add n_results=min(req.top_k, collection.count()) in the Vector Bridge's query handler.
No chain between WF01 → WF02 → WF03. WF02 and WF03 are webhook-only. Nothing automatically triggers them after ingestion completes. WF01 should end with an HTTP Request node calling WF02's webhook, and WF02 should chain to WF03. Currently you must manually trigger all three in sequence.
agent_runs.token_estimate is never populated. The column exists, but every insert sets it to null. With no token tracking, you have no visibility into cost or when you're approaching rate limits. Add a rough estimate in each Code node: Math.round(JSON.stringify(inputs).length / 4).
WF03's JSON parsing may double-parse. When Gemini's responseMimeType is "application/json", the n8n HTTP node may already parse the response as an object. Then JSON.parse(strategy) in the Code node will throw "SyntaxError: Unexpected token o". Test whether the text field is a string or already an object and handle both.
breakdown_key is omitted from WF01's INSERT. The column has DEFAULT 'none' so the insert works, but the UNIQUE constraint is on (date, entity_level, entity_id, breakdown_key). If you ever add breakdowns later, existing rows will conflict because they all use the implicit default. Be explicit: include breakdown_key in the INSERT as 'none' from day one.

💡 Optimizations
Pre-aggregate KPI data before sending to agents. Sending all 100 raw rows to Strategy Agent wastes tokens and dilutes signal. Instead: "Top 5 by spend, Bottom 5 by CPA, Any with frequency > threshold, 7-day trend summary." This could cut prompt size by 70% and produce sharper outputs.
Batch the WF02 embedding calls. Instead of looping through 500 documents sequentially (each requiring an HTTP round-trip), use n8n's "Split In Batches" node (batch size 10-20) with a Wait node between batches. This avoids rate limiting and is far faster overall.
Add a checksum guard in WF02. Before re-embedding a document, check if the checksum stored in Chroma's metadata matches the current document's MD5. Skip if unchanged. This prevents unnecessary Gemini API calls on every refresh.
Use a dedicated Copywriting → Compliance → Store sub-workflow rather than trying to squeeze it into the daily audit WF03. This makes the compliance pipeline independently testable and retryable.
Add a "kill switch" env variable. One boolean in the .env that disables all Meta write workflows globally, callable via n8n's /api/v1/workflows/{id}/activate endpoint. Documented in the PRD but not implemented.

📂 File-by-File Feedback
docker-compose.yml — Structurally correct. Missing: SLACK_WEBHOOK_URL, META_ACCESS_TOKEN, META_API_VERSION, TARGET_CPA, TARGET_ROAS, and other business config vars are referenced in workflows but not declared as n8n env vars in the compose file. Add them to the n8n service's environment block or document them as n8n workflow variables.
schema.sql — Clean and well-designed. Issues: action_plans.compliance_verdict has no CHECK constraint (should be CHECK (compliance_verdict IN ('PASS', 'FAIL', 'NEEDS_REVISION'))). Missing indexes on action_plans(status), actions_executed(plan_id), and agent_runs(agent_name, started_at) — these will be the most frequently filtered columns in practice.
01-ingestion.json — Core logic is correct but broken by the parallel merge bug (see Critical Issue #1). Also: the Alert on Failure node has no error path wired to it from any upstream node. n8n requires explicitly connecting the error output port of a node to the alert node.
02-embedding-refresh.json — The Postgres query is good (last 30 days, adset/ad level, 500 doc limit). Issues: (1) never calls the Sanitiser service, (2) no chain trigger from WF01, (3) $items().length in "Log Job Run" may reference the wrong scope — use $input.all().length instead.
03-daily-audit.json — Most problematic file. Three bugs: (1) Compliance Agent has no input (Critical #2), (2) Strategy Agent has no Merge (Critical #3), (3) no Copywriting Agent present despite being the only thing the Compliance Agent should review. The JSON parsing in "Assemble Report Bundle" is also fragile (see Improvements).
04-action-proposal.json — Missing: plan_id generation, Slack webhook receiver, Wait node for async approval. The compliance gate check $json.compliance_verdict is fine as a concept but the field path needs to match however WF03 actually passes data to WF04 (which is currently undefined — there's no trigger chain between them).
05-action-execution.json — The "Enforce Hard Rules" code checks action.conversions but the ActionPlan schema from WF03 never includes a conversions field per action — it only has entity_id, action_type, rationale, risk. This guard will never fire because the condition (action.conversions || 0) < minConversions always evaluates to 0 < 10 = true... wait no — it would block all scale actions since conversions is always 0. Fix: join conversions data from Postgres before running the guard.
compliance-agent.txt — Well-structured. But contradicts the marketing playbook (see Critical #8). The HARD-FAIL examples given in the prompt are word-for-word the hook examples in the marketing doc.
optimisation-agent.txt — References $env.TARGET_CPA, $env.TARGET_ROAS etc. These are fine as placeholders but the actual runtime injection happens in WF03's prompt construction node, not from this file directly. Make sure WF03 actually reads from n8n env variables and injects them before sending to Gemini.
app.py (Sanitiser) — Presidio setup is correct. Missing: spacy model download in Dockerfile (likely en_core_web_lg or en_core_web_sm — must be RUN python -m spacy download en_core_web_sm in Dockerfile). Without this, the service will crash on startup. No auth, no rate limiting, no request size limit (someone could POST a 10MB string).
app.py (Vector Bridge) — Functionally correct. Performance issues: new httpx client per call, get_collection() on every request. Auth gap. The /delete/{doc_id} endpoint is completely unprotected and can wipe any document with a single unauthenticated request.

🔄 Data Flow Problems
The intended flow is Meta API → Postgres → Chroma → Agents → Slack → Meta Writes. Here's where it actually breaks:
Break 1 (WF01 → Postgres): Data arrives incomplete because the Merge node is missing. Postgres receives 3 partial writes instead of 1 complete write.
Break 2 (WF01 → WF02): There is no trigger. WF02 must be manually invoked via webhook after WF01 completes.
Break 3 (Chroma → WF03 Strategy Agent): The Strategy Agent is triggered twice — once by the KPI query, once by the Chroma RAG results — without merging, so it uses half its intended context.
Break 4 (Copywriting → Compliance in WF03): The Compliance Agent reviews empty input. No copy is ever generated within WF03.
Break 5 (WF03 → WF04): No automatic trigger. WF04 must be manually POSTed to.
Break 6 (Slack button → WF05): The Slack approval callback has nowhere to land. WF05 is never triggered by approvals.
Break 7 (WF05 → audit log): The meta_api_response field is written as null because $json.response doesn't exist.
In its current state, the only workflow that could run end-to-end without manual intervention or crashing is WF02 in isolation (fetch from Postgres, basic sanitise, embed, upsert to Chroma).

🧠 Agent Design Issues
No Orchestrator Agent. The PRD specifies an Orchestrator that plans the task DAG, routes messages, and resolves conflicts. Instead, WF03 directly calls 3 agents in parallel with no coordination. If Strategy outputs a low-confidence result, Optimisation still runs regardless. There's no feedback loop.
Compliance Agent is checking ads that don't exist. It's wired to run during the daily audit but is supposed to review copywriting output — and there is no copywriting step in the audit. The Compliance Agent should run as a gate within the creative generation sub-flow, not as an afterthought in the daily audit.
Optimisation Agent doesn't get entity names, only IDs. The ActionPlan output includes entity_id but human reviewers in Slack see act_12345678 which is meaningless. The agent prompt should be given the entity name alongside the ID, and the Slack approval message should display the human-readable name.
No evaluator/critic loop. If any agent returns malformed JSON (despite the schema enforcement), JSON.parse in the Code node crashes the entire audit. A try/catch with a retry call to Gemini ("Your previous response was invalid JSON, please retry") would make the system far more resilient.
Prompts are static files, not versioned. The .txt prompt files have no version number. When you iterate the prompt, you have no way to know which version generated which audit. Store prompt_version in the agent_runs table and embed a version tag inside each prompt file.

🚀 Production Readiness Score
DimensionScoreReasonArchitecture5/10Good concept, clear separation of concerns, but missing Orchestrator, no agent feedback loops, parallel flows not mergedReliability2/10Broken data flow at 5 of 7 connection points, missing error paths, no retry on agent failures, WF01 parallel bug corrupts data silentlyScalability4/10No batching for embeddings, new HTTP client per embed call, no token budget, will hit Gemini rate limits at moderate volumeSafety4/10Compliance gates exist but are effectively disabled (no input). SQL injection throughout. No auth on internal APIs. Gemini free tier leaks ad data to GoogleMaintainability4/10No prompt versioning, no schema migration strategy, hard-coded magic values (e.g. INTERVAL '7 days', LIMIT 100), no monitoring
Overall: 3.8/10 — not deployable in current state.
The foundation is well-researched and the schema design, agent separation, and safety intent are all correct. But there are blocking bugs that would cause the system to either silently corrupt data (WF01 merge), never generate compliant copy (WF03), or leave approvals in permanent limbo (WF04). None of the 5 workflows chain automatically. Fix the 10 critical issues first, then the improvement items — the system can realistically reach 7/10 with 2-3 weeks of focused work.