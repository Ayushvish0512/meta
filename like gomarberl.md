📄 PRD: AI Meta Ads Growth Agent (MCP-style, Advanced)
1. 🎯 Objective

Build a multi-agent AI system that:

Connects to Meta Ads (like Meta MCP tools)
Goes beyond reporting → diagnoses, decides, and suggests execution
Improves:
Targeting
Creative strategy
Budget allocation
Generates:
Next ad creatives (copy + scripts)
Targeting experiments
Scaling decisions

👉 Core idea:
Not just “numbers → suggestions”
But numbers + creative + targeting + funnel understanding → actions

2. 🧠 Key Difference vs Marble MCP Tools
Feature	Marble MCP	Your Agent (Target)
Metrics reporting	✅	✅
Basic suggestions	✅	✅
Targeting intelligence	❌ limited	✅ deep
Creative generation	❌	✅ (core feature)
Script writing	❌	✅
Funnel understanding	❌	✅
Execution-ready plans	⚠️	✅

👉 You are building a full growth brain, not a dashboard AI.

3. 🏗️ Core System Modules
3.1 Data Layer (Same base as MCP tools)

Inputs:

Meta Ads API (campaign, adset, ad level)
Creative data (copies, hooks, videos)
Landing page data
Historical performance

Output:

Clean structured dataset
3.2 Analysis Engine (Upgrade over MCP)

Instead of just metrics → insights, add:

A. Performance Diagnosis
CPA, ROAS, CTR, CPM
Funnel drop-offs
Learning phase detection
B. Creative Intelligence
Hook performance
Fatigue detection
Angle classification (pain/benefit/emotional)
C. Targeting Intelligence (IMPORTANT ADDITION)
Audience overlap issues
Broad vs interest vs lookalike performance
Geo/device breakdown insights

👉 This is what MCP tools don’t deeply do.

4. 🤖 Multi-Agent System
4.1 Core Agents
1. Performance Analyst Agent
Reads Meta data
Finds:
Winners
Losers
Wasted spend

Output:

{
  "issues": [],
  "opportunities": []
}
2. Targeting Agent (🔥 Your key differentiator)

Analyzes:

Audience segments
Scaling potential
Missing audiences

Outputs:

New targeting ideas:
Interests
Lookalikes
Broad strategies

Example:

{
  "new_audiences": [
    "broad + advantage+",
    "LAL 1% purchasers",
    "interest stack: hormonal health + fitness"
  ]
}
3. Creative Strategist Agent

Analyzes:

Which hooks work
Which formats win

Outputs:

New angles:
Problem-focused
Emotional
Educational
4. Copy + Script Generator Agent

Generates:

Ad copies
Video scripts
Hooks

Example output:

{
  "hook": "Struggling with hormonal imbalance?",
  "script": "Start with a relatable problem..."
}
5. Optimisation Agent

Decides:

Scale / Pause / Test

Rules:

Based on CPA thresholds
Based on conversion volume
6. Experimentation Agent

Creates:

A/B testing roadmap

Example:

Test 3 hooks
Test 2 audiences
Test 1 landing page variation
5. 🔄 Workflow (Like MCP but deeper)
Daily Flow
Fetch Meta data
Analyze performance
Retrieve past learnings (RAG)
Run agents:
Performance
Targeting
Creative
Generate:
Report
Action plan
New ad creatives
6. 📊 Output (Final User Experience)
6.1 Daily Report
What’s working
What’s failing
Why
6.2 Action Plan
Pause X adsets
Scale Y campaigns
Test Z audiences
6.3 Creative Pack (🔥 Unique)
3 new hooks
2 ad copies
1 video script
6.4 Targeting Plan (🔥 Unique)
New audiences to test
Budget split suggestion
Funnel-level targeting advice
7. 🧩 Decision Intelligence (Important)
Hardcoded Rules (must have)
Min conversions before scaling
Budget increase limits
Fatigue thresholds
AI Decisions
Why performance changed
What to test next
Creative direction
8. ⚠️ Key Risks & Fixes
Problem 1: Generic AI suggestions

✅ Fix:

Use RAG with your past data
Problem 2: Wrong scaling decisions

✅ Fix:

Add strict rules (not only AI)
Problem 3: Weak targeting insights

✅ Fix:

Build dedicated targeting agent (most people skip this)
9. 🚀 MVP Scope (Build This First)

Phase 1:

Meta data ingestion
Performance analysis
Daily report

Phase 2:

Targeting suggestions
Creative insights

Phase 3:

Copy + script generation
Experiment planning
10. 🧠 Final Positioning

What you are building:

👉 Not a tool like Marble
👉 Not a reporting dashboard

👉 It is:

“AI Media Buyer + Creative Strategist + Growth Analyst”

🔥 Brutally Honest Insight

If you only:

Show metrics
Give suggestions

👉 You are just another MCP clone

If you:

Understand targeting deeply
Generate creatives
Suggest experiments

👉 Then you are building a real AI growth system