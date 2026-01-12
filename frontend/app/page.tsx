'use client';

import { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, RefreshCw, TrendingUp, TrendingDown, Users, Droplets } from 'lucide-react';
import { tokenApi, watchlistApi } from '@/lib/api';
import { TokenTable } from '@/components/tokens/TokenTable';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { formatNumber, formatLiquidity } from '@/lib/utils';

const USER_ID = 'default-user';

export default function Dashboard() {
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'watchlist'>('all');
  const [watchlist, setWatchlist] = useState<Set<string>>(new Set());
  const queryClient = useQueryClient();

  // Fetch all tokens
  const { data: tokens = [], isLoading, refetch } = useQuery({
    queryKey: ['tokens'],
    queryFn: tokenApi.listScored,
    refetchInterval: 60000,
  });

  // Fetch watchlist
  const { data: watchlistItems = [] } = useQuery({
    queryKey: ['watchlist', USER_ID],
    queryFn: () => watchlistApi.list(USER_ID),
  });

  // Update watchlist set when items change
  useEffect(() => {
    setWatchlist(new Set(watchlistItems.map((w) => w.mint_address)));
  }, [watchlistItems]);

  // Add to watchlist mutation
  const addToWatchlist = useMutation({
    mutationFn: (mint: string) => watchlistApi.add(USER_ID, mint),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watchlist'] }),
  });

  // Remove from watchlist mutation
  const removeFromWatchlist = useMutation({
    mutationFn: (mint: string) => watchlistApi.remove(USER_ID, mint),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watchlist'] }),
  });

  // Filter tokens by search
  const filteredTokens = tokens.filter(
    (t) =>
      t.symbol?.toLowerCase().includes(search.toLowerCase()) ||
      t.name?.toLowerCase().includes(search.toLowerCase()) ||
      t.mint_address.toLowerCase().includes(search.toLowerCase())
  );

  // Get watchlist tokens
  const watchlistTokens = tokens.filter((t) => watchlist.has(t.mint_address));

  // Toggle watchlist handler
  const handleToggleWatchlist = async (mint: string) => {
    if (watchlist.has(mint)) {
      await removeFromWatchlist.mutateAsync(mint);
      setWatchlist((prev) => {
        const next = new Set(prev);
        next.delete(mint);
        return next;
      });
    } else {
      await addToWatchlist.mutateAsync(mint);
      setWatchlist((prev) => new Set([...prev, mint]));
    }
  };

  // Stats
  const highScoreCount = tokens.filter((t) => (t.composite_score || 0) >= 70).length;
  const lowScoreCount = tokens.filter((t) => (t.composite_score || 0) < 40).length;
  const totalLiquidity = tokens.reduce((sum, t) => sum + (t.liquidity || 0), 0);
  const totalHolders = tokens.reduce((sum, t) => sum + (t.holder_count || 0), 0);

  const displayTokens = activeTab === 'all' ? filteredTokens : watchlistTokens;

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold">Token Dashboard</h2>
          <p className="text-muted-foreground">
            Track and score Solana meme tokens
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search tokens..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 w-64"
            />
          </div>
          <Button variant="outline" size="icon" onClick={() => refetch()}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              High Score (70+)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">{highScoreCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-500" />
              Low Score (&lt;40)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{lowScoreCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Droplets className="h-4 w-4 text-blue-500" />
              Total Liquidity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatLiquidity(totalLiquidity)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="h-4 w-4 text-purple-500" />
              Total Holders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(totalHolders)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-4 py-2 -mb-px border-b-2 transition-colors ${
            activeTab === 'all'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          All Tokens ({filteredTokens.length})
        </button>
        <button
          onClick={() => setActiveTab('watchlist')}
          className={`px-4 py-2 -mb-px border-b-2 transition-colors ${
            activeTab === 'watchlist'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Watchlist ({watchlist.size})
        </button>
      </div>

      {/* Token Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center text-muted-foreground">
              Loading tokens...
            </div>
          ) : (
            <TokenTable
              tokens={displayTokens}
              watchlist={watchlist}
              onToggleWatchlist={handleToggleWatchlist}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
