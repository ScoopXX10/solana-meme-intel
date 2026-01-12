/**
 * Utility functions for the frontend.
 */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with proper precedence.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a price for display.
 */
export function formatPrice(price: number | null | undefined): string {
  if (price === null || price === undefined) return '$0.00';
  if (price < 0.00001) return `$${price.toExponential(2)}`;
  if (price < 0.01) return `$${price.toFixed(8)}`;
  if (price < 1) return `$${price.toFixed(6)}`;
  return `$${price.toFixed(2)}`;
}

/**
 * Format a large number with abbreviations.
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '0';
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toLocaleString();
}

/**
 * Format liquidity for display.
 */
export function formatLiquidity(liq: number | null | undefined): string {
  if (liq === null || liq === undefined) return '$0';
  return `$${formatNumber(liq)}`;
}

/**
 * Get score color class based on value.
 */
export function getScoreColor(score: number | null | undefined): string {
  if (score === null || score === undefined) return 'text-gray-500';
  if (score >= 70) return 'text-green-500';
  if (score >= 40) return 'text-yellow-500';
  return 'text-red-500';
}

/**
 * Get score background color class.
 */
export function getScoreBgColor(score: number | null | undefined): string {
  if (score === null || score === undefined) return 'bg-gray-500';
  if (score >= 70) return 'bg-green-500';
  if (score >= 40) return 'bg-yellow-500';
  return 'bg-red-500';
}

/**
 * Truncate a mint address for display.
 */
export function truncateMint(mint: string, length: number = 8): string {
  if (mint.length <= length * 2) return mint;
  return `${mint.slice(0, length)}...${mint.slice(-length)}`;
}

/**
 * Format a timestamp for display.
 */
export function formatTime(timestamp: string | null | undefined): string {
  if (!timestamp) return 'Never';
  const date = new Date(timestamp);
  return date.toLocaleString();
}

/**
 * Get relative time string.
 */
export function getRelativeTime(timestamp: string | null | undefined): string {
  if (!timestamp) return 'Never';
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
