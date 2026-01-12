-- =====================================================
-- Solana Meme Intel - COMPLETE Database Schema
-- Run this ENTIRE script in Supabase SQL Editor
-- =====================================================

-- =====================================================
-- 1. TOKENS TABLE (main table)
-- =====================================================
CREATE TABLE IF NOT EXISTS tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mint_address TEXT UNIQUE NOT NULL,
    name TEXT,
    symbol TEXT,
    price DECIMAL,
    liquidity DECIMAL,
    holder_count INTEGER DEFAULT 0,

    -- Authority status
    mint_auth TEXT DEFAULT 'unknown',
    freeze_auth TEXT DEFAULT 'unknown',

    -- Holder metrics
    top10_pct DECIMAL,
    whale_count INTEGER,

    -- Scoring fields
    dev_score DECIMAL,
    holder_score DECIMAL,
    risk_score DECIMAL,
    meme_score DECIMAL,
    composite_score DECIMAL,

    -- Additional metrics for scoring
    age_days INTEGER,
    liq_pct DECIMAL,
    volume_24h DECIMAL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_tokens_mint ON tokens(mint_address);
CREATE INDEX IF NOT EXISTS idx_tokens_score ON tokens(composite_score DESC);


-- =====================================================
-- 2. WATCHLISTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    mint_address TEXT NOT NULL REFERENCES tokens(mint_address) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    UNIQUE(user_id, mint_address)
);

CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_mint ON watchlists(mint_address);


-- =====================================================
-- 3. TOKEN HISTORY TABLE (for charts)
-- =====================================================
CREATE TABLE IF NOT EXISTS token_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mint_address TEXT NOT NULL REFERENCES tokens(mint_address) ON DELETE CASCADE,
    price DECIMAL,
    liquidity DECIMAL,
    holder_count INTEGER,
    composite_score DECIMAL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_token_history_mint_time
ON token_history(mint_address, recorded_at DESC);


-- =====================================================
-- 4. HELPER FUNCTION for hourly snapshots
-- =====================================================
CREATE OR REPLACE FUNCTION record_token_snapshot()
RETURNS void AS $$
BEGIN
    INSERT INTO token_history (mint_address, price, liquidity, holder_count, composite_score)
    SELECT mint_address, price, liquidity, holder_count, composite_score
    FROM tokens
    WHERE price IS NOT NULL;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- 5. INSERT SAMPLE TOKENS (popular Solana meme coins)
-- =====================================================
INSERT INTO tokens (mint_address, symbol, name, price, liquidity, holder_count)
VALUES
    ('DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', 'BONK', 'Bonk', 0, 0, 0),
    ('EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm', 'WIF', 'dogwifhat', 0, 0, 0),
    ('7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr', 'POPCAT', 'Popcat', 0, 0, 0),
    ('ED5nyyWEzpPPiWimP8vYm7sD7TD3LAt3Q3gRTWHzPJBY', 'MOODENG', 'Moo Deng', 0, 0, 0),
    ('ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82', 'BOME', 'Book of Meme', 0, 0, 0),
    ('MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5', 'MEW', 'cat in a dogs world', 0, 0, 0),
    ('A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump', 'FARTCOIN', 'Fartcoin', 0, 0, 0),
    ('CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump', 'GOAT', 'Goatseus Maximus', 0, 0, 0)
ON CONFLICT (mint_address) DO NOTHING;


-- =====================================================
-- DONE! You should now have:
-- - tokens table with 8 sample meme coins
-- - watchlists table for user tracking
-- - token_history table for charts
-- - record_token_snapshot() function
-- =====================================================
