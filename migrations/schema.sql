CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY,
    request_id UUID NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(32) NOT NULL,
    comment TEXT NOT NULL,
    ai_provider VARCHAR(32) NOT NULL,
    ai_status VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    summary TEXT NOT NULL,
    suggested_reply TEXT NOT NULL,
    owner_email_status VARCHAR(20) NOT NULL,
    user_email_status VARCHAR(20) NOT NULL,
    owner_email_error TEXT NULL,
    user_email_error TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contacts_ai_status ON contacts (ai_status);
CREATE INDEX IF NOT EXISTS idx_contacts_category ON contacts (category);

CREATE TABLE IF NOT EXISTS rate_limits (
    client_key VARCHAR(64) PRIMARY KEY,
    window_started_at TIMESTAMPTZ NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 1,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_updated_at ON rate_limits (updated_at DESC);

