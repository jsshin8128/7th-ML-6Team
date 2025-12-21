import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { congestionColors, type TouristSpot } from '@/types/tourist';

interface ComparisonChartProps {
  spots: TouristSpot[];
}

export function ComparisonChart({ spots }: ComparisonChartProps) {
  const data = spots
    .map(spot => ({
      name: spot.name,
      visitors: spot.expectedVisitors,
      level: spot.congestionLevel,
    }))
    .sort((a, b) => b.visitors - a.visitors);

  return (
    <Card variant="elevated">
      <CardHeader>
        <CardTitle className="text-base">관광지 비교</CardTitle>
        <CardDescription>예상 방문자 수 기준</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={data} 
              layout="vertical"
              margin={{ top: 0, right: 10, left: 0, bottom: 0 }}
            >
              <XAxis 
                type="number" 
                tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}
              />
              <YAxis 
                type="category"
                dataKey="name"
                tick={{ fontSize: 11, fill: 'hsl(var(--foreground))' }}
                tickLine={false}
                axisLine={false}
                width={70}
              />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '12px',
                  boxShadow: 'var(--shadow-lg)'
                }}
                formatter={(value: number) => [`${value.toLocaleString()}명`, '예상 방문자']}
              />
              <Bar 
                dataKey="visitors" 
                radius={[0, 6, 6, 0]}
                barSize={24}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={congestionColors[entry.level]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
