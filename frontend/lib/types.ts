/**
 * TypeScript type definitions for the Solana Meme Intel frontend.
 */

export interface Token {
  mint_address: string;
  name: string | null;
  symbol: string | null;
  price: number;
  liquidity: number;
  holder_count: number;

  // Scores (0-100)
  dev_score: number | null;
  holder_score: number | null;
  risk_score: number | null;
  meme_score: number | null;
  composite_score: number | null;

  // Metadata
  created_at?: string;
  updated?: string;

  // Authority status
  mint_auth?: string;
  freeze_auth?: string;
}

export interface ScoreBreakdown {
  final_score: number;
  components: {
    dev_score: number;
    holder_score: number;
    risk_score: number;
    meme_score: number;
  };
}

export interface WatchlistItem {
  id: string;
  user_id: string;
  mint_address: string;
  added_at: string;
  notes: string | null;
  tokens?: Token;
}

export interface HistoryDataPoint {
  price: number;
  liquidity: number;
  holder_count: number;
  composite_score: number;
  recorded_at: string;
}

export type SortField = 'composite_score' | 'price' | 'liquidity' | 'holder_count' | 'updated';
export type SortDirection = 'asc' | 'desc';
