import { useNavigate, useLocation } from 'react-router-dom';
import { RefreshCw, BarChart3, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  onRefresh?: () => void;
  isLoading?: boolean;
}

export function Header({ onRefresh, isLoading }: HeaderProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const now = new Date();
  const timeString = now.toLocaleTimeString('ko-KR', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });
  const dateString = now.toLocaleDateString('ko-KR', {
    month: 'long',
    day: 'numeric',
    weekday: 'short'
  });

  const isHomePage = location.pathname === '/';

  return (
    <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-xl border-b border-border/50">
      <div className="container py-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-3 hover:opacity-80 transition-opacity"
          >
            {isHomePage ? (
              <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center shadow-toss-md p-1.5">
                <img src="/khuda-logo.png" alt="KHUDA" className="w-full h-full object-contain" />
              </div>
            ) : (
              <div className="w-10 h-10 rounded-xl bg-background border border-border/50 flex items-center justify-center shadow-toss-md hover:bg-muted/50 transition-colors">
                <ArrowLeft className="w-5 h-5 text-foreground" />
              </div>
            )}
            <div className="text-left">
              <div className="flex items-baseline gap-2">
                <h1 className="font-bold text-lg text-foreground">서울 관광 가이드</h1>
                <span className="text-[10px] text-muted-foreground font-normal">with KHUDA</span>
              </div>
              <p className="text-xs text-muted-foreground">실시간 혼잡도 예측</p>
            </div>
          </button>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium text-foreground">{timeString}</p>
              <p className="text-xs text-muted-foreground">{dateString}</p>
            </div>
            {isHomePage && (
              <Button 
                variant="ghost" 
                size="icon"
                className="rounded-xl"
                onClick={() => navigate('/settings/model-evaluation')}
                title="모델 평가"
              >
                <BarChart3 className="w-4 h-4" />
              </Button>
            )}
            {onRefresh && (
              <Button 
                variant="ghost" 
                size="icon"
                className="rounded-xl"
                onClick={onRefresh}
                disabled={isLoading}
                title="새로고침"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
