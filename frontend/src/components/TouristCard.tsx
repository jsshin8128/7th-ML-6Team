import { TrendingUp, TrendingDown, Minus, Users, MapPin } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { CongestionBadge } from './CongestionBadge';
import type { TouristSpot } from '@/types/tourist';

interface TouristCardProps {
  spot: TouristSpot;
  index: number;
  onClick?: () => void;
}

export function TouristCard({ spot, index, onClick }: TouristCardProps) {
  const TrendIcon = spot.trend === 'up' ? TrendingUp : spot.trend === 'down' ? TrendingDown : Minus;
  const trendColor = spot.trend === 'up' ? 'text-congestion-high' : spot.trend === 'down' ? 'text-congestion-low' : 'text-muted-foreground';

  return (
    <Card 
      variant="interactive" 
      className={`animate-fade-in opacity-0 stagger-${index + 1}`}
      onClick={onClick}
    >
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="space-y-1">
            <h3 className="font-semibold text-lg text-foreground">{spot.name}</h3>
            <p className="text-xs text-muted-foreground">{spot.nameEn}</p>
          </div>
          <CongestionBadge level={spot.congestionLevel} />
        </div>

        <p className="text-sm text-muted-foreground mb-4 line-clamp-1">
          {spot.description}
        </p>

        <div className="flex items-center gap-2 text-sm">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Users className="w-4 h-4 text-primary" />
          </div>
          <div>
            <p className="text-muted-foreground text-xs">예상 방문자</p>
            <div className="flex items-center gap-1">
              <span className="font-semibold text-foreground">
                {spot.expectedVisitors.toLocaleString()}
              </span>
              <TrendIcon className={`w-3 h-3 ${trendColor}`} />
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-border/50">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <MapPin className="w-3 h-3" />
            <span className="truncate">{spot.address}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
