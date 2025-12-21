import { useState, useMemo } from 'react';
import { Header } from '@/components/Header';
import { CongestionOverview } from '@/components/CongestionOverview';
import { RecommendationCard } from '@/components/RecommendationCard';
import { ModelPerformanceCard } from '@/components/ModelPerformanceCard';
import { TouristCard } from '@/components/TouristCard';
import { SpotDetail } from '@/components/SpotDetail';
import { ComparisonChart } from '@/components/ComparisonChart';
import { useTouristSpots, useAllPredictions } from '@/hooks/useTouristData';
import { useQueryClient } from '@tanstack/react-query';
import type { TouristSpot } from '@/types/tourist';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

const Index = () => {
  const [selectedSpot, setSelectedSpot] = useState<TouristSpot | null>(null);
  const queryClient = useQueryClient();
  const { spots, isLoading, error } = useTouristSpots();
  const { data: predictionsData } = useAllPredictions();

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['predictions'] });
    queryClient.invalidateQueries({ queryKey: ['tourist-sites'] });
  };

  const recommendedSpot = useMemo(() => {
    if (!spots || spots.length === 0) return null;
    
    const congestionPriority = { low: 0, normal: 1, high: 2, veryHigh: 3 };
    const sorted = [...spots].sort((a, b) => {
      const priorityDiff = congestionPriority[a.congestionLevel] - congestionPriority[b.congestionLevel];
      if (priorityDiff !== 0) return priorityDiff;
      return a.expectedVisitors - b.expectedVisitors;
    });
    
    return sorted[0] || null;
  }, [spots]);

  if (error) {
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
    const isConnectionError = errorMessage.includes('연결할 수 없습니다') || errorMessage.includes('Failed to fetch');
    
    return (
      <div className="min-h-screen bg-background">
        <Header onRefresh={handleRefresh} isLoading={false} />
        <main className="container py-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-medium">데이터를 불러오는 중 오류가 발생했습니다.</p>
                {isConnectionError && (
                  <div className="text-sm space-y-1">
                    <p>백엔드 서버가 실행 중인지 확인해주세요:</p>
                    <ul className="list-disc list-inside space-y-1 ml-2">
                      <li>백엔드 서버가 <code className="bg-muted px-1 rounded">http://localhost:8000</code>에서 실행 중인지 확인</li>
                      <li>터미널에서 <code className="bg-muted px-1 rounded">python backend/main.py</code> 또는 <code className="bg-muted px-1 rounded">uvicorn backend.main:app --reload</code> 실행</li>
                      <li>브라우저에서 <a href="http://localhost:8000/api/health" target="_blank" rel="noopener noreferrer" className="text-primary underline">http://localhost:8000/api/health</a> 접속 테스트</li>
                    </ul>
                  </div>
                )}
                <p className="text-xs text-muted-foreground mt-2">
                  오류 상세: {errorMessage}
                </p>
              </div>
            </AlertDescription>
          </Alert>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header onRefresh={handleRefresh} isLoading={isLoading} />
      
      <main className="container py-6 space-y-6">
        <section>
          {isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : (
            <CongestionOverview spots={spots} />
          )}
        </section>

        {!isLoading && recommendedSpot && (
          <section>
            <RecommendationCard 
              recommendedSpot={recommendedSpot}
              onSpotClick={setSelectedSpot}
            />
          </section>
        )}

        <section>
          <ModelPerformanceCard />
        </section>

        <section>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-semibold text-lg text-foreground">관광지별 현황</h2>
              <p className="text-sm text-muted-foreground">터치하여 상세 정보 확인</p>
            </div>
          </div>
          
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(7)].map((_, index) => (
                <Skeleton key={index} className="h-48 w-full" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {spots.map((spot, index) => (
                <TouristCard 
                  key={spot.id} 
                  spot={spot} 
                  index={index}
                  onClick={() => setSelectedSpot(spot)}
                />
              ))}
            </div>
          )}
        </section>

        <section>
          {isLoading ? (
            <Skeleton className="h-64 w-full" />
          ) : (
            <ComparisonChart spots={spots} />
          )}
        </section>

        <footer className="text-center py-8 border-t border-border/50">
          <p className="text-xs text-muted-foreground">
            © 2025 Seoul Tour Guide · 데이터는 실시간 예측값입니다
            {predictionsData?.timestamp && (
              <span className="block mt-1">
                마지막 업데이트: {new Date(predictionsData.timestamp).toLocaleString('ko-KR')}
              </span>
            )}
          </p>
        </footer>
      </main>

      {selectedSpot && (
        <SpotDetail spot={selectedSpot} onClose={() => setSelectedSpot(null)} />
      )}
    </div>
  );
};

export default Index;
