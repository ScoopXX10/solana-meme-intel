/**
 * API client for Solana Meme Intel backend.
 */
import axios from 'axios';
import { Token, ScoreBreakdown, WatchlistItem, HistoryDataPoint } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token endpoints
export const tokenApi = {
  list: async (): Promise<Token[]> => {
    const { data } = await api.get('/tokens/');
    return data;
  },

  listScored: async (): Promise<Token[]> => {
    const { data } = await api.get('/tokens/scored');
    return data;
  },

  get: async (mint: string): Promise<Token> => {
    const { data } = await api.get(`/tokens/${mint}`);
    return data;
  },

  refresh: async (mint: string): Promise<{ token: Token; scores: ScoreBreakdown }> => {
    const { data } = await api.post(`/tokens/refresh/${mint}`);
    return data;
  },

  getScore: async (mint: string): Promise<ScoreBreakdown> => {
    const { data } = await api.get(`/score/${mint}`);
    return data.scores;
  },
};

// Watchlist endpoints
export const watchlistApi = {
  list: async (userId: string): Promise<WatchlistItem[]> => {
    const { data } = await api.get(`/watchlist/${userId}`);
    return data;
  },

  add: async (userId: string, mint: string): Promise<WatchlistItem> => {
    const { data } = await api.post(`/watchlist/${userId}`, { mint_address: mint });
    return data;
  },

  remove: async (userId: string, mint: string): Promise<void> => {
    await api.delete(`/watchlist/${userId}/${mint}`);
  },

  check: async (userId: string, mint: string): Promise<boolean> => {
    const { data } = await api.get(`/watchlist/${userId}/check/${mint}`);
    return data.in_watchlist;
  },
};

// History endpoints
export const historyApi = {
  get: async (mint: string, hours: number = 24): Promise<HistoryDataPoint[]> => {
    const { data } = await api.get(`/history/${mint}`, { params: { hours } });
    return data;
  },

  getLatest: async (mint: string, limit: number = 10): Promise<HistoryDataPoint[]> => {
    const { data } = await api.get(`/history/${mint}/latest`, { params: { limit } });
    return data;
  },
};

export default api;
