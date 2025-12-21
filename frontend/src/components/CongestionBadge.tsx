import { Badge } from '@/components/ui/badge';
import { CongestionLevel, congestionLabels } from '@/types/tourist';

interface CongestionBadgeProps {
  level: CongestionLevel;
  showDot?: boolean;
  size?: 'sm' | 'md';
}

const variantMap: Record<CongestionLevel, 'low' | 'normal' | 'high' | 'veryHigh'> = {
  low: 'low',
  normal: 'normal',
  high: 'high',
  veryHigh: 'veryHigh',
};

export function CongestionBadge({ level, showDot = true, size = 'md' }: CongestionBadgeProps) {
  return (
    <Badge 
      variant={variantMap[level]}
      className={size === 'sm' ? 'text-[10px] px-2 py-0.5' : ''}
    >
      {showDot && (
        <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 animate-pulse-soft" />
      )}
      {congestionLabels[level]}
    </Badge>
  );
}
