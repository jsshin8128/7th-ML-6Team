import { useState } from 'react';
import { Header } from '@/components/Header';
import { CongestionOverview } from '@/components/CongestionOverview';
import { TouristCard } from '@/components/TouristCard';
import { SpotDetail } from '@/components/SpotDetail';
import { ComparisonChart } from '@/components/ComparisonChart';
import { touristSpots } from '@/data/touristSpots';
import type { TouristSpot } from '@/types/tourist';

const Index = () => {
  const [selectedSpot, setSelectedSpot] = useState<TouristSpot | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="min-h-screen bg-background">
      <Header onRefresh={handleRefresh} isLoading={isRefreshing} />
      
      <main className="container py-6 space-y-6">
        {/* Overview Section */}
        <section>
          <CongestionOverview />
        </section>

        {/* Tourist Spots Grid */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-semibold text-lg text-foreground">관광지별 현황</h2>
              <p className="text-sm text-muted-foreground">터치하여 상세 정보 확인</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {touristSpots.map((spot, index) => (
              <TouristCard 
                key={spot.id} 
                spot={spot} 
                index={index}
                onClick={() => setSelectedSpot(spot)}
              />
            ))}
          </div>
        </section>

        {/* Comparison Chart */}
        <section>
          <ComparisonChart />
        </section>

        {/* Footer */}
        <footer className="text-center py-8 border-t border-border/50">
          <p className="text-xs text-muted-foreground">
            © 2024 Seoul Tour Guide · 데이터는 실시간 예측값입니다
          </p>
        </footer>
      </main>

      {/* Detail Modal */}
      {selectedSpot && (
        <SpotDetail spot={selectedSpot} onClose={() => setSelectedSpot(null)} />
      )}
    </div>
  );
};

export default Index;
