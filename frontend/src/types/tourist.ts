export type CongestionLevel = 'low' | 'normal' | 'high' | 'veryHigh';

export interface TouristSpot {
  id: string;
  name: string;
  nameEn: string;
  description: string;
  congestionLevel: CongestionLevel;
  expectedVisitors: number;
  trend: 'up' | 'down' | 'stable';
  hourlyData: { hour: string; visitors: number }[];
  address: string;
}

export const congestionLabels: Record<CongestionLevel, string> = {
  low: '여유',
  normal: '보통',
  high: '혼잡',
  veryHigh: '매우혼잡',
};

export const congestionColors: Record<CongestionLevel, string> = {
  low: 'hsl(160, 84%, 39%)',
  normal: 'hsl(45, 93%, 47%)',
  high: 'hsl(25, 95%, 53%)',
  veryHigh: 'hsl(0, 84%, 60%)',
};
