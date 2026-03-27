-- Laiqa Growth Agent - Canonical Schema

CREATE TABLE IF NOT EXISTS meta_entities (
    entity_id TEXT PRIMARY KEY,
    entity_level TEXT NOT NULL CHECK (entity_level IN ('campaign', 'adset', 'ad')),
    name TEXT,
    status TEXT,
    objective TEXT,
    parent_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meta_insights_daily (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    entity_level TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    breakdown_key TEXT DEFAULT 'none',
    impressions BIGINT DEFAULT 0,
    reach BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    spend NUMERIC(12,4) DEFAULT 0,
    conversions INT DEFAULT 0,
    frequency NUMERIC(8,4) GENERATED ALWAYS AS (
        CASE WHEN reach > 0 THEN impressions::NUMERIC / reach ELSE 0 END
    ) STORED,
    ctr NUMERIC(8,6) GENERATED ALWAYS AS (
        CASE WHEN impressions > 0 THEN clicks::NUMERIC / impressions ELSE 0 END
    ) STORED,
    cpa NUMERIC(12,4) GENERATED ALWAYS AS (
        CASE WHEN conversions > 0 THEN spend / conversions ELSE NULL END
    ) STORED,
    raw_json JSONB,
    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (date, entity_level, entity_id, breakdown_key)
);

CREATE INDEX IF NOT EXISTS idx_insights_date_entity ON meta_insights_daily (date, entity_level, entity_id);

CREATE TABLE IF NOT EXISTS creative_assets (
    creative_id TEXT PRIMARY KEY,
    ad_id TEXT,
    asset_type TEXT,
    hook TEXT,
    body_copy TEXT,
    cta TEXT,
    landing_url TEXT,
    compliance_tags TEXT[],
    compliance_status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    hypothesis TEXT NOT NULL,
    variants JSONB,
    start_date DATE,
    end_date DATE,
    success_criteria JSONB,
    decision TEXT,
    outcome_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_runs (
    run_id TEXT PRIMARY KEY,
    correlation_id TEXT,
    agent_name TEXT NOT NULL,
    task_type TEXT,
    inputs_hash TEXT,
    outputs_json JSONB,
    schema_valid BOOLEAN,
    token_estimate INT,
    status TEXT DEFAULT 'RUNNING',
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS action_plans (
    plan_id TEXT PRIMARY KEY,
    correlation_id TEXT,
    date DATE NOT NULL,
    account_id TEXT,
    actions JSONB NOT NULL,
    guardrails JSONB,
    evidence_refs TEXT[],
    compliance_verdict TEXT,
    status TEXT DEFAULT 'PENDING_APPROVAL',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS approvals (
    approval_id SERIAL PRIMARY KEY,
    plan_id TEXT REFERENCES action_plans(plan_id),
    approver TEXT,
    decision TEXT CHECK (decision IN ('APPROVED', 'REJECTED', 'CHANGES_REQUESTED')),
    notes TEXT,
    decided_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS actions_executed (
    execution_id SERIAL PRIMARY KEY,
    plan_id TEXT REFERENCES action_plans(plan_id),
    entity_level TEXT,
    entity_id TEXT,
    action_type TEXT,
    meta_api_call JSONB,
    meta_api_response JSONB,
    rollback_ref JSONB,
    status TEXT DEFAULT 'PENDING',
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS embedding_job_runs (
    job_id SERIAL PRIMARY KEY,
    doc_type TEXT,
    doc_count INT,
    checksum TEXT,
    status TEXT,
    ran_at TIMESTAMPTZ DEFAULT NOW()
);
