-- =====================================================
-- Solana Meme Intel - Database Schema
-- Run these statements in Supabase SQL Editor
-- =====================================================

-- Watchlist table for user token tracking
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    mint_address TEXT NOT NULL REFERENCES tokens(mint_address) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    UNIQUE(user_id, mint_address)
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_mint ON watchlists(mint_address);


-- Token history table for price/liquidity charts
CREATE TABLE IF NOT EXISTS token_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mint_address TEXT NOT NULL REFERENCES tokens(mint_address) ON DELETE CASCADE,
    price DECIMAL,
    liquidity DECIMAL,
    holder_count INTEGER,
    composite_score DECIMAL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for time-series queries
CREATE INDEX IF NOT EXISTS idx_token_history_mint_time
ON token_history(mint_address, recorded_at DESC);


-- Function to record token snapshots (called hourly by scheduler)
CREATE OR REPLACE FUNCTION record_token_snapshot()
RETURNS void AS $$
BEGIN
    INSERT INTO token_history (mint_address, price, liquidity, holder_count, composite_score)
    SELECT mint_address, price, liquidity, holder_count, composite_score
    FROM tokens
    WHERE price IS NOT NULL;
END;
$$ LANGUAGE plpgsql;


-- Add new columns to tokens table if not present
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS mint_auth TEXT DEFAULT 'unknown';
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS freeze_auth TEXT DEFAULT 'unknown';
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS top10_pct DECIMAL;
ALTER TABLE tokens ADD COLUMN IF NOT EXISTS whale_count INTEGER;


-- Enable Row Level Security (optional but recommended)
-- ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can manage their own watchlists" ON watchlists
--     FOR ALL USING (auth.uid()::text = user_id);
