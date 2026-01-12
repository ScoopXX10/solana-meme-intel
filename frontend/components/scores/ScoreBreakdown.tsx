'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Token } from '@/lib/types';
import { getScoreColor, getScoreBgColor } from '@/lib/utils';

interface ScoreBreakdownProps {
  token: Token;
}

const scoreConfig = [
  { key: 'dev_score', label: 'Developer Score', weight: '30%', description: 'Wallet age, track record, behavior' },
  { key: 'holder_score', label: 'Holder Score', weight: '25%', description: 'Distribution, whale concentration' },
  { key: 'risk_score', label: 'Risk Score', weight: '25%', description: 'Authority status, liquidity' },
  { key: 'meme_score', label: 'Meme Score', weight: '20%', description: 'Social velocity, engagement' },
];

export function ScoreBreakdown({ token }: ScoreBreakdownProps) {
  const compositeScore = token.composite_score ?? 0;
  const scoreColor = getScoreColor(token.composite_score);
  const scoreBg = getScoreBgColor(token.composite_score);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Score Breakdown</span>
          <span className={`text-3xl font-bold ${scoreColor}`}>
            {compositeScore.toFixed(1)}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {scoreConfig.map(({ key, label, weight, description }) => {
          const value = (token[key as keyof Token] as number | null) ?? 0;
          const color = getScoreColor(value);

          return (
            <div key={key} className="space-y-2">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-medium">{label}</span>
                  <span className="text-xs text-muted-foreground ml-2">({weight})</span>
                </div>
                <span className={`font-bold ${color}`}>
                  {value.toFixed(0)}
                </span>
              </div>
              <Progress value={value} indicatorClassName={getScoreBgColor(value)} />
              <p className="text-xs text-muted-foreground">{description}</p>
            </div>
          );
        })}

        <div className="pt-4 border-t border-border">
          <div className="flex justify-between items-center">
            <span className="font-semibold">Composite Score</span>
            <div className={`px-3 py-1 rounded-full text-white font-bold ${scoreBg}`}>
              {compositeScore.toFixed(1)} / 100
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Weighted average: 30% Dev + 25% Holder + 25% Risk + 20% Meme
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
