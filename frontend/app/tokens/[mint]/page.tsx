'use client';

import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, ExternalLink, RefreshCw, Star, StarOff, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { tokenApi, watchlistApi, historyApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScoreBreakdown } from '@/components/scores/ScoreBreakdown';
import { formatPrice, formatLiquidity, formatNumber, getRelativeTime, truncateMint } from '@/lib/utils';

const USER_ID = 'default-user';

export default function TokenDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const mint = params.mint as string;
  const [copied, setCopied] = useState(false);

  // Fetch token data
  const { data: token, isLoading, refetch } = useQuery({
    queryKey: ['token', mint],
    queryFn: () => tokenApi.get(mint),
    enabled: !!mint,
  });

  // Check watchlist status
  const { data: inWatchlist } = useQuery({
    queryKey: ['watchlist-check', mint],
    queryFn: () => watchlistApi.check(USER_ID, mint),
    enabled: !!mint,
  });

  // Fetch history
  const { data: history = [] } = useQuery({
    queryKey: ['history', mint],
    queryFn: () => historyApi.get(mint, 24),
    enabled: !!mint,
  });

  // Refresh mutation
  const refreshMutation = useMutation({
    mutationFn: () => tokenApi.refresh(mint),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['token', mint] });
      queryClient.invalidateQueries({ queryKey: ['history', mint] });
    },
  });

  // Watchlist mutations
  const addToWatchlist = useMutation({
    mutationFn: () => watchlistApi.add(USER_ID, mint),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watchlist-check', mint] }),
  });

  const removeFromWatchlist = useMutation({
    mutationFn: () => watchlistApi.remove(USER_ID, mint),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watchlist-check', mint] }),
  });

  const handleCopyMint = async () => {
    await navigator.clipboard.writeText(mint);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleToggleWatchlist = () => {
    if (inWatchlist) {
      removeFromWatchlist.mutate();
    } else {
      addToWatchlist.mutate();
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-6">
        <div className="text-center text-muted-foreground py-12">
          Loading token details...
        </div>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="container mx-auto px-4 py-6">
        <div className="text-center py-12">
          <h2 className="text-xl font-bold mb-2">Token Not Found</h2>
          <p className="text-muted-foreground mb-4">
            The token with mint address {truncateMint(mint)} was not found.
          </p>
          <Button onClick={() => router.push('/')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Button variant="ghost" size="sm" onClick={() => router.push('/')} className="mb-2">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{token.symbol || 'Unknown'}</h1>
            <Badge variant="outline">{token.name || 'Unknown Token'}</Badge>
          </div>
          <div className="flex items-center gap-2 mt-2 text-sm text-muted-foreground">
            <code className="bg-muted px-2 py-1 rounded">{truncateMint(mint, 12)}</code>
            <Button variant="ghost" size="icon" className="h-6 w-6" onClick={handleCopyMint}>
              {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
            </Button>
            <a
              href={`https://solscan.io/token/${mint}`}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleToggleWatchlist}
            disabled={addToWatchlist.isPending || removeFromWatchlist.isPending}
          >
            {inWatchlist ? (
              <>
                <Star className="mr-2 h-4 w-4 fill-yellow-400 text-yellow-400" />
                Watching
              </>
            ) : (
              <>
                <StarOff className="mr-2 h-4 w-4" />
                Watch
              </>
            )}
          </Button>
          <Button
            onClick={() => refreshMutation.mutate()}
            disabled={refreshMutation.isPending}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Left Column - Stats */}
        <div className="space-y-6">
          {/* Price & Liquidity */}
          <Card>
            <CardHeader>
              <CardTitle>Market Data</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Price</div>
                  <div className="text-2xl font-bold font-mono">
                    {formatPrice(token.price)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Liquidity</div>
                  <div className="text-2xl font-bold font-mono">
                    {formatLiquidity(token.liquidity)}
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Holders</div>
                  <div className="text-xl font-bold">
                    {formatNumber(token.holder_count)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Last Updated</div>
                  <div className="text-sm">
                    {getRelativeTime(token.updated)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Authority Status */}
          <Card>
            <CardHeader>
              <CardTitle>Security Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Mint Authority</div>
                  <Badge variant={token.mint_auth === 'renounced' ? 'default' : 'destructive'}>
                    {token.mint_auth || 'Unknown'}
                  </Badge>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Freeze Authority</div>
                  <Badge variant={token.freeze_auth === 'renounced' ? 'default' : 'destructive'}>
                    {token.freeze_auth || 'Unknown'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* History Preview */}
          {history.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent History (24h)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">
                  {history.length} data points recorded
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Score */}
        <div>
          <ScoreBreakdown token={token} />
        </div>
      </div>
    </div>
  );
}
