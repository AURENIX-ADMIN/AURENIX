-- Migration: 002_research_schema
-- Description: Stores intelligence gathered by the Sentinel R&D Agent.
CREATE TABLE IF NOT EXISTS research_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    summary TEXT,
    source TEXT NOT NULL,
    -- 'arxiv', 'github', etc.
    score INTEGER,
    -- 0-100 Relevance Score
    published_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Optional: Vector embedding field if pgvector is enabled
    -- embedding vector(1536),
    metadata JSONB DEFAULT '{}'
);
-- Index for fast retrieval of high-score items
CREATE INDEX IF NOT EXISTS idx_research_score ON research_items(score DESC);
CREATE INDEX IF NOT EXISTS idx_research_source ON research_items(source);
-- RLS Policies
ALTER TABLE research_items ENABLE ROW LEVEL SECURITY;
-- Allow read access to authenticated users (Dashboard)
CREATE POLICY "Authenticated users can view research" ON research_items FOR
SELECT USING (
        auth.role() = 'authenticated'
        OR auth.role() = 'service_role'
    );
-- Allow insert access to service role (Sentinel Agent)
CREATE POLICY "Service role can insert research" ON research_items FOR
INSERT WITH CHECK (true);
-- In real prod, restrict to service_role strictly