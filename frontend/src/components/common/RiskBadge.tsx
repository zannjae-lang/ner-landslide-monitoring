import React from 'react';
import { RiskLevel } from '../../types';
import { ShieldCheck, Eye, AlertTriangle, AlertOctagon } from 'lucide-react';

interface RiskBadgeProps {
  level: RiskLevel | string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'md', showIcon = true }) => {
  const getStyle = () => {
    switch (level) {
      case 'Normal':
        return {
          bg: 'bg-[#EDF3EE] text-[#5C7A61] border-[#C8D8CB]',
          dot: 'bg-[#5C7A61]',
          icon: <ShieldCheck className="w-3.5 h-3.5 text-[#5C7A61]" />,
        };
      case 'Watch':
        return {
          bg: 'bg-[#FAF5EB] text-[#B18A3A] border-[#E5D5B3]',
          dot: 'bg-[#B18A3A]',
          icon: <Eye className="w-3.5 h-3.5 text-[#B18A3A]" />,
        };
      case 'Alert':
        return {
          bg: 'bg-[#FCF2EC] text-[#C96B3D] border-[#ECC5B0]',
          dot: 'bg-[#C96B3D]',
          icon: <AlertTriangle className="w-3.5 h-3.5 text-[#C96B3D]" />,
        };
      case 'Critical':
        return {
          bg: 'bg-[#FBF0F0] text-[#A83F3F] border-[#E8B8B8]',
          dot: 'bg-[#A83F3F]',
          icon: <AlertOctagon className="w-3.5 h-3.5 text-[#A83F3F]" />,
        };
      default:
        return {
          bg: 'bg-[#E9E6DD] text-[#5F665F] border-[#D5D2C8]',
          dot: 'bg-[#5F665F]',
          icon: null,
        };
    }
  };

  const style = getStyle();
  const sizeClasses = {
    sm: 'text-[10px] px-1.5 py-0.5',
    md: 'text-xs font-semibold px-2 py-0.5',
    lg: 'text-xs font-bold px-2.5 py-1',
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1 rounded border font-mono ${style.bg} ${sizeClasses}`}
    >
      {showIcon && style.icon}
      <span>{level?.toUpperCase() || 'UNKNOWN'}</span>
    </span>
  );
};
