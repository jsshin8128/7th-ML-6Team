import { X, Users, MapPin, TrendingUp, TrendingDown, Minus, Clock, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CongestionBadge } from './CongestionBadge';
import type { TouristSpot } from '@/types/tourist';

interface SpotDetailProps {
  spot: TouristSpot;
  onClose: () => void;
}

export function SpotDetail({ spot, onClose }: SpotDetailProps) {
  const TrendIcon = spot.trend === 'up' ? TrendingUp : spot.trend === 'down' ? TrendingDown : Minus;
  const trendText = spot.trend === 'up' ? '증가 추세' : spot.trend === 'down' ? '감소 추세' : '유지';

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm animate-fade-in">
      <div className="fixed inset-x-0 bottom-0 z-50 bg-card rounded-t-3xl shadow-toss-xl max-h-[85vh] overflow-auto animate-slide-up">
        <div className="sticky top-0 bg-card/95 backdrop-blur-sm z-10 px-5 pt-5 pb-3 border-b border-border/50">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-xl font-bold text-foreground">{spot.name}</h2>
                <CongestionBadge level={spot.congestionLevel} />
              </div>
              <p className="text-sm text-muted-foreground">{spot.nameEn}</p>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose} className="rounded-xl -mt-1">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        <div className="p-5 space-y-5">
          <div className="grid grid-cols-2 gap-3">
            <Card variant="flat" className="p-4 text-center">
              <Users className="w-5 h-5 mx-auto mb-2 text-primary" />
              <p className="text-lg font-bold text-foreground">{spot.expectedVisitors.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">예상 방문자</p>
            </Card>
            <Card variant="flat" className="p-4 text-center">
              <TrendIcon className="w-5 h-5 mx-auto mb-2 text-primary" />
              <p className="text-lg font-bold text-foreground">{trendText}</p>
              <p className="text-xs text-muted-foreground">방문 추세</p>
            </Card>
          </div>

          <Card variant="default">
            <CardHeader>
              <CardTitle className="text-base">시간대별 방문자 예측</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-48 flex flex-col items-center justify-center gap-3">
                <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center">
                  <BarChart3 className="w-8 h-8 text-muted-foreground" />
                </div>
                <div className="flex flex-col items-center gap-1">
                  <p className="text-sm font-medium text-muted-foreground">추후 반영 예정</p>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground/80">
                    <Clock className="w-3.5 h-3.5" />
                    <span>개발 진행 중</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="flat">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <MapPin className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium text-foreground mb-1">위치</p>
                  <p className="text-sm text-muted-foreground">{spot.address}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="pb-6">
            <p className="text-sm text-muted-foreground leading-relaxed">{spot.description}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
