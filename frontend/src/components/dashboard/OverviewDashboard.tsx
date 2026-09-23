import React from 'react';
import {
  MapPin,
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  CloudRain,
  Eye,
  ArrowUpRight,
  TrendingUp,
  Layers,
  Activity,
} from 'lucide-react';
import { Location, MapFeatureProperty, RiskLevel } from '../../types';
import { RiskBadge } from '../common/RiskBadge';

interface OverviewDashboardProps {
  locations: Location[];
  mapFeatures: MapFeatureProperty[];
  activeAlerts: any[];
  selectedStationId?: string | null;
  onSelectStation: (locationId: string) => void;
  onNavigateTab: (tab: string) => void;
}

const NER_STATES = [
  'Arunachal Pradesh',
  'Assam',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Sikkim',
  'Tripura',
];

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  locations,
  mapFeatures,
  activeAlerts,
  selectedStationId,
  onSelectStation,
  onNavigateTab,
}) => {
  const activeStationFeature =
    (selectedStationId ? mapFeatures.find((f) => f.location_id === selectedStationId) : null) ||
    mapFeatures[0];
  const activeStationLoc = locations.find(
    (l) => l.id === (activeStationFeature?.location_id || selectedStationId)
  );

  const totalMonitored = locations.length;
  const criticalCount = mapFeatures.filter((f) => f.final_risk === 'Critical').length;
  const alertCount = mapFeatures.filter((f) => f.final_risk === 'Alert').length;
  const watchCount = mapFeatures.filter((f) => f.final_risk === 'Watch').length;
  const normalCount = mapFeatures.filter((f) => f.final_risk === 'Normal').length;

  const stateStats = NER_STATES.map((state) => {
    const stateFeatures = mapFeatures.filter((f) => f.state === state);
    const stationCount = stateFeatures.length;
    const maxScore = stateFeatures.reduce((max, f) => Math.max(max, f.combined_risk_score), 0);
    const hasCritical = stateFeatures.some((f) => f.final_risk === 'Critical');
    const hasAlert = stateFeatures.some((f) => f.final_risk === 'Alert');
    const hasWatch = stateFeatures.some((f) => f.final_risk === 'Watch');

    let stateLevel: RiskLevel = 'Normal';
    if (hasCritical) stateLevel = 'Critical';
    else if (hasAlert) stateLevel = 'Alert';
    else if (hasWatch) stateLevel = 'Watch';

    const maxRain = stateFeatures.reduce((max, f) => Math.max(max, f.rainfall_24h_mm), 0);

    return {
      state,
      stationCount,
      stateLevel,
      maxScore,
      maxRain,
    };
  });

  return (
    <div className="space-y-4">
      {/* Top Regional Operational Banner */}
      <div className="earth-panel p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-[#5C7A61]" />
            <h2 className="text-sm font-bold tracking-tight text-[#20251F]">
              Northeast Regional Landslide Threat Status
            </h2>
          </div>
          <p className="text-xs text-[#5F665F] max-w-3xl">
            Real-time multi-sensor intelligence fusing static XGBoost susceptibility (Model 1), dynamic precipitation windows (Model 2), and antecedent hydrology across 8 North Eastern states.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={() => onNavigateTab('map')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] font-semibold text-xs transition-colors font-mono"
          >
            <Layers className="w-3.5 h-3.5" />
            Launch 8-State GIS Map
          </button>
        </div>
      </div>

      {/* Active Corridor Situational Intelligence Spotlight */}
      {activeStationFeature && (
        <div className="earth-panel p-4 border-[#806B52]/40 bg-[#FAF9F5] shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-[#D5D2C8] pb-3 mb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[#806B52]">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#E9E6DD] text-[#496A52] font-bold border border-[#D5D2C8]">
                    Active Station Spotlight
                  </span>
                  <RiskBadge level={activeStationFeature.final_risk} size="sm" />
                </div>
                <h3 className="text-sm font-black text-[#20251F] font-sans mt-0.5">
                  {activeStationFeature.name} ({activeStationFeature.district}, {activeStationFeature.state})
                </h3>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  onSelectStation(activeStationFeature.location_id);
                  onNavigateTab('monitoring');
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] text-xs font-semibold transition-colors font-mono"
              >
                Inspect Telemetry Console <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* 4 Multi-Model Insights Metrics for Selected Station */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 font-mono text-xs">
            <div className="p-3 rounded bg-[#E9E6DD]/60 border border-[#D5D2C8]">
              <span className="text-[10px] text-[#5F665F] block mb-0.5 uppercase font-bold">
                1. Fused Threat Score
              </span>
              <div className="text-base font-black text-[#20251F]">
                {(activeStationFeature.combined_risk_score * 100).toFixed(0)}%
              </div>
              <span className="text-[10px] text-[#806B52] block mt-0.5 font-sans">
                Level: {activeStationFeature.final_risk}
              </span>
            </div>

            <div className="p-3 rounded bg-[#E9E6DD]/60 border border-[#D5D2C8]">
              <span className="text-[10px] text-[#5F665F] block mb-0.5 uppercase font-bold">
                2. Model 1 (Static Susc.)
              </span>
              <div className="text-base font-black text-[#20251F]">
                {(activeStationFeature.susceptibility_probability * 100).toFixed(1)}%
              </div>
              <span className="text-[10px] text-[#5F665F] block mt-0.5 font-sans">
                Class: {activeStationFeature.susceptibility_class}
              </span>
            </div>

            <div className="p-3 rounded bg-[#E9E6DD]/60 border border-[#D5D2C8]">
              <span className="text-[10px] text-[#5F665F] block mb-0.5 uppercase font-bold">
                3. Model 2 (Dynamic Trigger)
              </span>
              <div className="text-base font-black text-[#20251F]">
                {(activeStationFeature.dynamic_probability * 100).toFixed(1)}%
              </div>
              <span className="text-[10px] text-[#5F665F] block mt-0.5 font-sans">
                {activeStationFeature.warning_candidate ? 'Trigger: CANDIDATE' : 'Trigger: Baseline'}
              </span>
            </div>

            <div className="p-3 rounded bg-[#E9E6DD]/60 border border-[#D5D2C8]">
              <span className="text-[10px] text-[#5F665F] block mb-0.5 uppercase font-bold">
                4. 24h Rain / Terrain
              </span>
              <div className="text-base font-black text-[#55758A]">
                {activeStationFeature.rainfall_24h_mm.toFixed(1)} mm
              </div>
              <span className="text-[10px] text-[#5F665F] block mt-0.5 font-sans">
                Elev: {activeStationLoc?.elevation_m || activeStationFeature.elevation_m || 820}m &bull; Slope: {activeStationLoc?.slope_deg || activeStationFeature.slope_deg || 34}°
              </span>
            </div>
          </div>
        </div>
      )}

      {/* KPI Threat Matrix Row */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-2.5 font-mono">
        <div className="earth-panel p-3">
          <div className="flex items-center justify-between text-[#5F665F] text-xs mb-1 font-medium font-sans">
            <span>Monitored Corridors</span>
            <MapPin className="w-3.5 h-3.5 text-[#806B52]" />
          </div>
          <div className="text-lg font-black text-[#20251F]">{totalMonitored}</div>
          <div className="text-[10px] text-[#889087] mt-0.5">8 Northeast States</div>
        </div>

        <div className="earth-panel p-3 border-[#E8B8B8] bg-[#FBF0F0]">
          <div className="flex items-center justify-between text-[#A83F3F] text-xs mb-1 font-medium font-sans">
            <span>Critical Threat (≥0.75)</span>
            <AlertOctagon className="w-3.5 h-3.5 text-[#A83F3F]" />
          </div>
          <div className="text-lg font-black text-[#A83F3F]">{criticalCount}</div>
          <div className="text-[10px] text-[#A83F3F] mt-0.5 font-sans">Evacuation advisory</div>
        </div>

        <div className="earth-panel p-3 border-[#ECC5B0] bg-[#FCF2EC]">
          <div className="flex items-center justify-between text-[#C96B3D] text-xs mb-1 font-medium font-sans">
            <span>Alert Threat (≥0.50)</span>
            <AlertTriangle className="w-3.5 h-3.5 text-[#C96B3D]" />
          </div>
          <div className="text-lg font-black text-[#C96B3D]">{alertCount}</div>
          <div className="text-[10px] text-[#C96B3D] mt-0.5 font-sans">Highway preparedness</div>
        </div>

        <div className="earth-panel p-3 border-[#E5D5B3] bg-[#FAF5EB]">
          <div className="flex items-center justify-between text-[#B18A3A] text-xs mb-1 font-medium font-sans">
            <span>Watch Threat (≥0.25)</span>
            <Eye className="w-3.5 h-3.5 text-[#B18A3A]" />
          </div>
          <div className="text-lg font-black text-[#B18A3A]">{watchCount}</div>
          <div className="text-[10px] text-[#B18A3A] mt-0.5 font-sans">Elevated precipitation</div>
        </div>

        <div className="earth-panel p-3 border-[#C8D8CB] bg-[#EDF3EE] col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between text-[#5C7A61] text-xs mb-1 font-medium font-sans">
            <span>Normal Baseline (&lt;0.25)</span>
            <ShieldCheck className="w-3.5 h-3.5 text-[#5C7A61]" />
          </div>
          <div className="text-lg font-black text-[#5C7A61]">{normalCount}</div>
          <div className="text-[10px] text-[#5C7A61] mt-0.5 font-sans">Stable hydrological baseline</div>
        </div>
      </div>

      {/* 8-State Risk Status Grid */}
      <div className="earth-panel p-4">
        <div className="flex items-center justify-between mb-3 border-b border-[#D5D2C8] pb-2.5">
          <div>
            <h3 className="text-xs font-bold text-[#20251F] uppercase font-mono flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-[#496A52]" />
              Northeastern States Threat Aggregation
            </h3>
            <p className="text-xs text-[#5F665F]">
              State-level aggregated threat index derived from real-time terrain & weather sensors.
            </p>
          </div>
          <span className="text-[10px] font-mono text-[#5F665F] bg-[#E9E6DD] px-2 py-0.5 rounded border border-[#D5D2C8]">
            8 States Monitored
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
          {stateStats.map((item) => (
            <div
              key={item.state}
              className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8] hover:border-[#806B52] transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-xs text-[#20251F]">{item.state}</h4>
                  <span className="text-[10px] text-[#889087] font-mono">{item.stationCount} Stations</span>
                </div>
                <RiskBadge level={item.stateLevel} size="sm" />
              </div>

              <div className="mt-2.5 pt-1.5 border-t border-[#E2DFD5] flex items-center justify-between text-[10px] font-mono">
                <span className="text-[#55758A] flex items-center gap-1">
                  <CloudRain className="w-3 h-3 text-[#55758A]" />
                  {item.maxRain.toFixed(1)} mm
                </span>
                <span className="text-[#20251F] font-semibold">
                  Peak: {(item.maxScore * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dual Panel: Active Alert Feed & Station Priority Ledger */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Active Operational Alerts */}
        <div className="earth-panel p-4 lg:col-span-1 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2.5 border-b border-[#D5D2C8] pb-2">
              <h3 className="text-xs font-bold text-[#20251F] uppercase font-mono flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-[#B18A3A]" />
                Active Early Warnings ({activeAlerts.length})
              </h3>
              <button
                onClick={() => onNavigateTab('alerts')}
                className="text-xs text-[#496A52] hover:underline flex items-center gap-1 font-mono font-semibold"
              >
                Ledger <ArrowUpRight className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
              {activeAlerts.length === 0 ? (
                <div className="text-center py-8 text-[#889087] text-xs font-mono">
                  <ShieldCheck className="w-6 h-6 mx-auto mb-1.5 text-[#5C7A61]" />
                  No active critical early warnings at this time.
                </div>
              ) : (
                activeAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    onClick={() => {
                      onSelectStation(alert.location_id);
                      onNavigateTab('monitoring');
                    }}
                    className={`p-2.5 rounded border transition-colors cursor-pointer ${
                      activeStationFeature?.location_id === alert.location_id
                        ? 'bg-[#E9E6DD] border-[#496A52] shadow-xs'
                        : 'bg-[#FAF9F5] border-[#D5D2C8] hover:border-[#806B52]'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-[#20251F]">{alert.location_name}</span>
                      <RiskBadge level={alert.severity} size="sm" />
                    </div>
                    <p className="text-[11px] text-[#5F665F] line-clamp-2 leading-relaxed">{alert.message}</p>
                    <div className="mt-1.5 text-[10px] font-mono text-[#889087] flex items-center justify-between">
                      <span>{alert.state}</span>
                      <span className="text-[#55758A]">Rain: {alert.rainfall_24h_mm?.toFixed(1)} mm</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-2.5 pt-2 border-t border-[#E2DFD5] text-[10px] font-mono text-[#889087]">
            * Trigger: Threat Score ≥ 0.25 (Watch) generates automated operational dispatch.
          </div>
        </div>

        {/* Priority Station Telemetry Table */}
        <div className="earth-panel p-4 lg:col-span-2">
          <div className="flex items-center justify-between mb-2.5 border-b border-[#D5D2C8] pb-2">
            <div>
              <h3 className="text-xs font-bold text-[#20251F] uppercase font-mono flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-[#496A52]" />
                Station Dual-Model Telemetry Stream
              </h3>
              <p className="text-xs text-[#5F665F]">
                Live dual-model inference outputs across critical hill corridors.
              </p>
            </div>
            <button
              onClick={() => onNavigateTab('monitoring')}
              className="text-xs text-[#496A52] hover:underline flex items-center gap-1 font-mono font-semibold"
            >
              Console <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[10px] text-[#5F665F] border-b border-[#D5D2C8] bg-[#E9E6DD] font-mono uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-2 px-3">Station / Region</th>
                  <th className="py-2 px-3">Model 1 (Susc.)</th>
                  <th className="py-2 px-3">Model 2 (Dyn.)</th>
                  <th className="py-2 px-3">24h Rain</th>
                  <th className="py-2 px-3">Fused Threat</th>
                  <th className="py-2 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2DFD5] font-mono">
                {/* Ensure active station is displayed at the top if present */}
                {(() => {
                  const sorted = [...mapFeatures].sort((a, b) => {
                    if (a.location_id === activeStationFeature?.location_id) return -1;
                    if (b.location_id === activeStationFeature?.location_id) return 1;
                    return b.combined_risk_score - a.combined_risk_score;
                  });

                  return sorted.slice(0, 7).map((f) => {
                    const isSelected = f.location_id === activeStationFeature?.location_id;
                    return (
                      <tr
                        key={f.location_id}
                        onClick={() => onSelectStation(f.location_id)}
                        className={`transition-colors cursor-pointer ${
                          isSelected
                            ? 'bg-[#E9E6DD] border-l-3 border-l-[#496A52]'
                            : 'hover:bg-[#E9E6DD]/50'
                        }`}
                      >
                        <td className="py-2 px-3">
                          <div className="font-sans font-bold text-[#20251F] text-xs flex items-center gap-1.5">
                            {f.name}
                            {isSelected && (
                              <span className="text-[9px] px-1 py-0.2 rounded bg-[#17201B] text-[#FAF9F5] font-mono">
                                ACTIVE
                              </span>
                            )}
                          </div>
                          <div className="text-[10px] text-[#889087] font-sans">
                            {f.district}, {f.state}
                          </div>
                        </td>
                        <td className="py-2 px-3">
                          <span className="text-[#20251F]">
                            {(f.susceptibility_probability * 100).toFixed(1)}%
                          </span>
                          <span className="text-[10px] text-[#889087] block font-sans">
                            {f.susceptibility_class}
                          </span>
                        </td>
                        <td className="py-2 px-3">
                          <span className="text-[#20251F]">
                            {(f.dynamic_probability * 100).toFixed(1)}%
                          </span>
                          <span className="text-[10px] text-[#889087] block font-sans">
                            {f.warning_candidate ? 'Candidate: YES' : 'Candidate: NO'}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-[#55758A] font-semibold">
                          {f.rainfall_24h_mm.toFixed(1)} mm
                        </td>
                        <td className="py-2 px-3">
                          <RiskBadge level={f.final_risk} size="sm" />
                        </td>
                        <td className="py-2 px-3 text-right font-sans">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectStation(f.location_id);
                              onNavigateTab('monitoring');
                            }}
                            className="px-2 py-0.5 rounded bg-[#FAF9F5] hover:bg-[#17201B] hover:text-[#FAF9F5] text-[#20251F] text-[11px] font-medium border border-[#D5D2C8] transition-colors"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    );
                  });
                })()}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
