import { X, Users, Clock, MapPin, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CongestionBadge } from './CongestionBadge';
import type { TouristSpot } from '@/types/tourist';
import { congestionColors } from '@/types/tourist';

interface SpotDetailProps {
  spot: TouristSpot;
  onClose: () => void;
}

export function SpotDetail({ spot, onClose }: SpotDetailProps) {
  const TrendIcon = spot.trend === 'up' ? TrendingUp : spot.trend === 'down' ? TrendingDown : Minus;
  const trendText = spot.trend === 'up' ? '증가 추세' : spot.trend === 'down' ? '감소 추세' : '유지';
  const chartColor = congestionColors[spot.congestionLevel];

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
          {/* Stats */}
          <div className="grid grid-cols-3 gap-3">
            <Card variant="flat" className="p-4 text-center">
              <Users className="w-5 h-5 mx-auto mb-2 text-primary" />
              <p className="text-lg font-bold text-foreground">{spot.expectedVisitors.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">예상 방문자</p>
            </Card>
            <Card variant="flat" className="p-4 text-center">
              <Clock className="w-5 h-5 mx-auto mb-2 text-primary" />
              <p className="text-lg font-bold text-foreground">{spot.peakHour}</p>
              <p className="text-xs text-muted-foreground">피크 시간</p>
            </Card>
            <Card variant="flat" className="p-4 text-center">
              <TrendIcon className="w-5 h-5 mx-auto mb-2 text-primary" />
              <p className="text-lg font-bold text-foreground">{trendText}</p>
              <p className="text-xs text-muted-foreground">방문 추세</p>
            </Card>
          </div>

          {/* Chart */}
          <Card variant="default">
            <CardHeader>
              <CardTitle className="text-base">시간대별 방문자 예측</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={spot.hourlyData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id={`gradient-${spot.id}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={chartColor} stopOpacity={0.3} />
                        <stop offset="100%" stopColor={chartColor} stopOpacity={0.05} />
                      </linearGradient>
                    </defs>
                    <XAxis 
                      dataKey="hour" 
                      tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis 
                      tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '12px',
                        boxShadow: 'var(--shadow-lg)'
                      }}
                      formatter={(value: number) => [`${value.toLocaleString()}명`, '방문자']}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="visitors" 
                      stroke={chartColor}
                      strokeWidth={2}
                      fill={`url(#gradient-${spot.id})`}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Location */}
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

          {/* Description */}
          <div className="pb-6">
            <p className="text-sm text-muted-foreground leading-relaxed">{spot.description}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
