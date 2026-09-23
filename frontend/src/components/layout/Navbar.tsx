import React, { useEffect, useState } from 'react';
import {
  Clock,
  ShieldAlert,
  Bell,
  RefreshCw,
  MapPin,
} from 'lucide-react';
import { Location, SystemHealth } from '../../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  systemHealth: SystemHealth | null;
  activeAlertCount: number;
  locations: Location[];
  selectedStationId: string | null;
  onSelectStation: (locationId: string) => void;
  onRefreshData: () => void;
  refreshing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  systemHealth,
  activeAlertCount,
  locations,
  selectedStationId,
  onSelectStation,
  onRefreshData,
  refreshing,
}) => {
  const [currentTime, setCurrentTime] = useState<string>('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString('en-IN', {
          timeZone: 'Asia/Kolkata',
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        })
      );
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return 'Regional Situational Awareness';
      case 'map':
        return '8-State GIS Landslide Threat Map';
      case 'monitoring':
        return 'Station Telemetry & Dual-Model Console';
      case 'alerts':
        return 'Early Warning Alert Queue & Incidents';
      case 'models':
        return 'Model Artifact Registry & Verification';
      case 'datasources':
        return 'Data Providers & Telemetry Health';
      default:
        return 'NER Landslide Operations';
    }
  };

  return (
    <header className="sticky top-0 z-30 border-b border-[#D5D2C8] bg-[#FAF9F5]/95 backdrop-blur-xs">
      {/* Top Advisory Strip */}
      <div className="bg-[#E9E6DD] border-b border-[#D5D2C8] px-4 py-1 flex items-center justify-between text-[11px] font-mono">
        <div className="flex items-center gap-2 text-[#5F665F]">
          <ShieldAlert className="w-3.5 h-3.5 text-[#B18A3A] flex-shrink-0" />
          <span className="text-[#806B52] font-semibold">SIH 26001 PROTOYPE:</span>
          <span className="hidden md:inline text-[#5F665F]">
            Uncalibrated research models &bull; Combined static susceptibility + dynamic rainfall early warning
          </span>
        </div>

        <div className="flex items-center gap-4 text-[#5F665F]">
          <span className="flex items-center gap-1.5">
            <Clock className="w-3 h-3 text-[#55758A]" />
            <span className="text-[#20251F] font-bold">{currentTime} IST</span>
          </span>
          <span className="text-[#D5D2C8] hidden sm:inline">&bull;</span>
          <span className="text-[#5F665F] hidden sm:inline">8 NER States Monitored</span>
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="px-4 sm:px-6 h-13 flex items-center justify-between py-2.5">
        {/* Current View Title */}
        <div>
          <h1 className="text-sm font-bold text-[#20251F] tracking-tight flex items-center gap-2 font-sans">
            {getPageTitle()}
          </h1>
          <p className="text-[11px] text-[#5F665F] font-mono">
            Ministry of Development of North Eastern Region (MDoNER)
          </p>
        </div>

        {/* Right Station Selector & Quick Controls */}
        <div className="flex items-center gap-2">
          {/* Station Quick Switcher */}
          {locations.length > 0 && (
            <div className="hidden md:flex items-center gap-1.5 bg-[#FAF9F5] border border-[#D5D2C8] px-2.5 py-1 rounded text-xs font-mono">
              <MapPin className="w-3.5 h-3.5 text-[#806B52]" />
              <select
                value={selectedStationId || ''}
                onChange={(e) => onSelectStation(e.target.value)}
                className="bg-transparent text-[#20251F] text-xs font-medium focus:outline-none cursor-pointer max-w-[180px] truncate"
              >
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id} className="bg-[#FAF9F5] text-[#20251F]">
                    {loc.name} ({loc.district})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Alert Quick Badge */}
          {activeAlertCount > 0 && (
            <button
              onClick={() => setActiveTab('alerts')}
              className="flex items-center gap-1.5 px-2.5 py-1 bg-[#FBF0F0] hover:bg-[#F5E1E1] text-[#A83F3F] border border-[#E8B8B8] rounded text-xs font-semibold font-mono transition-colors"
            >
              <Bell className="w-3.5 h-3.5 text-[#A83F3F]" />
              <span>{activeAlertCount} CRITICAL/WATCH</span>
            </button>
          )}

          {/* Refresh Action */}
          <button
            onClick={onRefreshData}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1 rounded bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] text-xs font-medium transition-colors disabled:opacity-50 font-mono"
            title="Refresh sensor data & predictions"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-[#FAF9F5]' : 'text-[#AEB4AA]'}`} />
            <span className="hidden sm:inline">{refreshing ? 'Syncing...' : 'Sync Data'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
