'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Star, StarOff, ArrowUpDown, ExternalLink } from 'lucide-react';
import { Token, SortField, SortDirection } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatPrice, formatLiquidity, formatNumber, getScoreBgColor, truncateMint } from '@/lib/utils';

interface TokenTableProps {
  tokens: Token[];
  watchlist: Set<string>;
  onToggleWatchlist: (mint: string) => void;
}

export function TokenTable({ tokens, watchlist, onToggleWatchlist }: TokenTableProps) {
  const [sortField, setSortField] = useState<SortField>('composite_score');
  const [sortDir, setSortDir] = useState<SortDirection>('desc');

  const sortedTokens = [...tokens].sort((a, b) => {
    const aVal = a[sortField] ?? 0;
    const bVal = b[sortField] ?? 0;
    return sortDir === 'desc' ? (bVal as number) - (aVal as number) : (aVal as number) - (bVal as number);
  });

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(sortDir === 'desc' ? 'asc' : 'desc');
    } else {
      setSortField(field);
      setSortDir('desc');
    }
  };

  const getScoreBadge = (score: number | null) => {
    if (score === null) return <Badge variant="secondary">N/A</Badge>;
    const bgColor = getScoreBgColor(score);
    return (
      <Badge className={`${bgColor} text-white`}>
        {score.toFixed(0)}
      </Badge>
    );
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border">
            <th className="w-12 p-3"></th>
            <th className="p-3 text-left font-medium">Token</th>
            <th className="p-3 text-right">
              <Button variant="ghost" size="sm" onClick={() => toggleSort('price')}>
                Price <ArrowUpDown className="ml-1 h-3 w-3" />
              </Button>
            </th>
            <th className="p-3 text-right">
              <Button variant="ghost" size="sm" onClick={() => toggleSort('liquidity')}>
                Liquidity <ArrowUpDown className="ml-1 h-3 w-3" />
              </Button>
            </th>
            <th className="p-3 text-right">
              <Button variant="ghost" size="sm" onClick={() => toggleSort('holder_count')}>
                Holders <ArrowUpDown className="ml-1 h-3 w-3" />
              </Button>
            </th>
            <th className="p-3 text-center">
              <Button variant="ghost" size="sm" onClick={() => toggleSort('composite_score')}>
                Score <ArrowUpDown className="ml-1 h-3 w-3" />
              </Button>
            </th>
            <th className="p-3 w-12"></th>
          </tr>
        </thead>
        <tbody>
          {sortedTokens.map((token) => (
            <tr key={token.mint_address} className="border-b border-border hover:bg-muted/50">
              <td className="p-3">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onToggleWatchlist(token.mint_address)}
                  className="h-8 w-8"
                >
                  {watchlist.has(token.mint_address) ? (
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ) : (
                    <StarOff className="h-4 w-4 text-muted-foreground" />
                  )}
                </Button>
              </td>
              <td className="p-3">
                <Link href={`/tokens/${token.mint_address}`} className="hover:underline">
                  <div className="font-medium">{token.symbol || 'Unknown'}</div>
                  <div className="text-sm text-muted-foreground">{token.name || truncateMint(token.mint_address)}</div>
                </Link>
              </td>
              <td className="p-3 text-right font-mono text-sm">
                {formatPrice(token.price)}
              </td>
              <td className="p-3 text-right font-mono text-sm">
                {formatLiquidity(token.liquidity)}
              </td>
              <td className="p-3 text-right font-mono text-sm">
                {formatNumber(token.holder_count)}
              </td>
              <td className="p-3 text-center">
                {getScoreBadge(token.composite_score)}
              </td>
              <td className="p-3">
                <a
                  href={`https://solscan.io/token/${token.mint_address}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {sortedTokens.length === 0 && (
        <div className="p-8 text-center text-muted-foreground">
          No tokens found
        </div>
      )}
    </div>
  );
}
