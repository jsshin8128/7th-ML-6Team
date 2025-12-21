import { Card, CardContent } from '@/components/ui/card';
import { touristSpots } from '@/data/touristSpots';
import { congestionLabels, type CongestionLevel } from '@/types/tourist';

const levelOrder: CongestionLevel[] = ['low', 'normal', 'high', 'veryHigh'];

const levelStyles: Record<CongestionLevel, { bg: string; text: string; border: string }> = {
  low: { bg: 'bg-congestion-low/10', text: 'text-congestion-low', border: 'border-congestion-low/30' },
  normal: { bg: 'bg-congestion-normal/10', text: 'text-congestion-normal', border: 'border-congestion-normal/30' },
  high: { bg: 'bg-congestion-high/10', text: 'text-congestion-high', border: 'border-congestion-high/30' },
  veryHigh: { bg: 'bg-congestion-very-high/10', text: 'text-congestion-very-high', border: 'border-congestion-very-high/30' },
};

export function CongestionOverview() {
  const counts = levelOrder.map(level => ({
    level,
    count: touristSpots.filter(spot => spot.congestionLevel === level).length
  }));

  const totalVisitors = touristSpots.reduce((sum, spot) => sum + spot.expectedVisitors, 0);

  return (
    <div className="space-y-4">
      <Card variant="elevated" className="overflow-hidden">
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-semibold text-foreground">오늘의 현황</h2>
              <p className="text-xs text-muted-foreground mt-0.5">전체 관광지 혼잡도 요약</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary">{totalVisitors.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">총 예상 방문자</p>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-2">
            {counts.map(({ level, count }) => (
              <div 
                key={level}
                className={`rounded-xl p-3 text-center border ${levelStyles[level].bg} ${levelStyles[level].border}`}
              >
                <p className={`text-2xl font-bold ${levelStyles[level].text}`}>{count}</p>
                <p className="text-xs text-muted-foreground mt-1">{congestionLabels[level]}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
