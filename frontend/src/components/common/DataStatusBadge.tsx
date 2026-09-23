import React from 'react';
import { DataQualityStatus } from '../../types';
import { CheckCircle2, Clock, AlertCircle, Cpu } from 'lucide-react';

interface DataStatusBadgeProps {
  status: DataQualityStatus | string;
  ageHours?: number;
}

export const DataStatusBadge: React.FC<DataStatusBadgeProps> = ({ status, ageHours }) => {
  const getBadge = () => {
    switch (status) {
      case 'Fresh':
        return {
          bg: 'bg-[#EDF3EE] text-[#496A52] border-[#C8D8CB]',
          icon: <CheckCircle2 className="w-3 h-3 text-[#496A52]" />,
          label: ageHours !== undefined ? `Fresh (${ageHours.toFixed(1)}h)` : 'Fresh Data',
        };
      case 'Stale':
        return {
          bg: 'bg-[#FAF5EB] text-[#B18A3A] border-[#E5D5B3]',
          icon: <Clock className="w-3 h-3 text-[#B18A3A]" />,
          label: ageHours !== undefined ? `Stale (${ageHours.toFixed(1)}h)` : 'Stale Data',
        };
      case 'Provisional/Demo':
        return {
          bg: 'bg-[#EBF1F5] text-[#55758A] border-[#C2D4E0]',
          icon: <Cpu className="w-3 h-3 text-[#55758A]" />,
          label: 'Simulated / Prototype',
        };
      case 'Unavailable':
      default:
        return {
          bg: 'bg-[#FBF0F0] text-[#A83F3F] border-[#E8B8B8]',
          icon: <AlertCircle className="w-3 h-3 text-[#A83F3F]" />,
          label: 'Data Unavailable',
        };
    }
  };

  const badge = getBadge();

  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono border ${badge.bg}`}
      title={status}
    >
      {badge.icon}
      <span>{badge.label}</span>
    </span>
  );
};
