import React, { useState, useEffect } from 'react';
import {
  Building2,
  Navigation,
  School,
  ShieldAlert,
  Loader2,
} from 'lucide-react';
import { api } from '../../services/api';

interface ExposureAssessmentPanelProps {
  locationId: string;
  latitude: number;
  longitude: number;
  locationName?: string;
}

export const ExposureAssessmentPanel: React.FC<ExposureAssessmentPanelProps> = ({
  locationId,
  latitude,
  longitude,
  locationName,
}) => {
  const [exposureData, setExposureData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [bufferMeters, setBufferMeters] = useState<number>(1000);

  const fetchExposure = async (radius: number = 1000) => {
    setLoading(true);
    try {
      const data = await api.analyzeExposure({
        location_id: locationId,
        latitude,
        longitude,
        location_name: locationName,
        buffer_radius_meters: radius,
      });
      setExposureData(data);
    } catch (err) {
      console.error('Failed to analyze infrastructure exposure', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (locationId) {
      fetchExposure(bufferMeters);
    }
  }, [locationId, bufferMeters]);

  if (loading) {
    return (
      <div className="earth-panel p-5 flex items-center justify-center space-x-2 text-[#5F665F] py-8 font-mono text-xs">
        <Loader2 className="w-4 h-4 animate-spin text-[#496A52]" />
        <span>Querying infrastructure exposure & transport lifelines...</span>
      </div>
    );
  }

  if (!exposureData) {
    return (
      <div className="earth-panel p-3.5 flex items-center justify-between text-xs">
        <span className="text-[#5F665F]">Infrastructure exposure analysis available.</span>
        <button
          onClick={() => fetchExposure(bufferMeters)}
          className="px-2.5 py-1 bg-[#FAF9F5] hover:bg-[#E9E6DD] text-[#496A52] rounded border border-[#D5D2C8] font-semibold text-xs font-mono"
        >
          Analyze Exposure
        </button>
      </div>
    );
  }

  const getExposureBadge = (level: string = 'Moderate') => {
    const l = level?.toLowerCase();
    if (l.includes('severe') || l.includes('critical') || l.includes('high')) {
      return 'text-[#A83F3F] bg-[#FBF0F0] border-[#E8B8B8]';
    }
    if (l.includes('moderate')) {
      return 'text-[#B18A3A] bg-[#FAF5EB] border-[#E5D5B3]';
    }
    return 'text-[#5C7A61] bg-[#EDF3EE] border-[#C8D8CB]';
  };

  const exposedAssets: any[] = exposureData.exposed_assets || [];
  const roadAssets = exposedAssets.filter(
    (a) => a.asset_type === 'HIGHWAY' || a.asset_type === 'STATE_ROAD'
  );
  const settlementAssets = exposedAssets.filter(
    (a) => a.asset_type === 'SETTLEMENT'
  );
  const criticalAssets = exposedAssets.filter(
    (a) => a.asset_type === 'BRIDGE' || a.asset_type === 'SCHOOL' || a.asset_type === 'HOSPITAL' || a.asset_type === 'RAILWAY'
  );

  const nearestRoadDist = roadAssets.length > 0
    ? Math.min(...roadAssets.map((r) => r.distance_meters))
    : null;

  return (
    <div className="earth-panel p-4 space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 border-b border-[#D5D2C8] pb-2.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[#806B52]">
            <Building2 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">
              Infrastructure & Population Exposure
            </h3>
            <p className="text-[11px] text-[#5F665F]">
              Vulnerability assessment of transport arteries, settlements, and civil assets
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-[10px] font-mono text-[#5F665F]">BUFFER:</span>
          <select
            value={bufferMeters}
            onChange={(e) => setBufferMeters(Number(e.target.value))}
            className="bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded px-2 py-0.5 font-mono focus:outline-none"
          >
            <option value={500}>500 m</option>
            <option value={1000}>1,000 m (Standard)</option>
            <option value={2000}>2,000 m (Corridor)</option>
          </select>
        </div>
      </div>

      {/* Summary Score Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 font-mono">
        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
          <span className="text-[10px] font-semibold text-[#5F665F] uppercase tracking-wider block mb-0.5">
            Exposure Rating
          </span>
          <div className="text-base font-black text-[#20251F] mb-1">
            {exposureData.exposure_risk_rating || 'Moderate Exposure'}
          </div>
          <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${getExposureBadge(exposureData.exposure_risk_rating)}`}>
            {exposureData.total_exposed_assets ?? exposedAssets.length} Assets in Buffer
          </span>
        </div>

        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
          <span className="text-[10px] font-semibold text-[#5F665F] uppercase tracking-wider block mb-0.5">
            Road Proximity
          </span>
          <div className="text-lg font-black text-[#55758A] mb-0.5">
            {nearestRoadDist !== null ? `${nearestRoadDist.toFixed(0)} m` : 'Adjacent'}
          </div>
          <span className="text-[10px] text-[#5F665F] font-sans">
            {roadAssets.length} road lifelines identified
          </span>
        </div>

        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
          <span className="text-[10px] font-semibold text-[#5F665F] uppercase tracking-wider block mb-0.5">
            Civil Settlements
          </span>
          <div className="text-lg font-black text-[#806B52] mb-0.5">
            {settlementAssets.length}
          </div>
          <span className="text-[10px] text-[#5F665F] font-sans">
            ~{settlementAssets.reduce((sum, s) => sum + (s.estimated_population_impact || 250), 0)} est. inhabitants
          </span>
        </div>

        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
          <span className="text-[10px] font-semibold text-[#5F665F] uppercase tracking-wider block mb-0.5">
            Critical Assets
          </span>
          <div className="text-lg font-black text-[#68754A] mb-0.5">
            {exposureData.critical_infrastructure_count ?? criticalAssets.length}
          </div>
          <span className="text-[10px] text-[#5F665F] font-sans">
            {criticalAssets.length} civil facilities in buffer
          </span>
        </div>
      </div>

      {/* Exposed Assets Breakdown Lists */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
        {/* Road & Highway Arteries */}
        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
          <h4 className="font-bold text-xs text-[#20251F] mb-2 flex items-center gap-1.5 font-mono uppercase">
            <Navigation className="w-3.5 h-3.5 text-[#55758A]" />
            Exposed Road Arteries & Lifelines ({roadAssets.length})
          </h4>
          <div className="space-y-1.5">
            {roadAssets.length > 0 ? (
              roadAssets.map((road: any, idx: number) => (
                <div key={idx} className="p-2 rounded bg-[#E9E6DD]/70 border border-[#D5D2C8] flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-[#20251F] block text-xs">{road.name}</span>
                    <span className="text-[10px] text-[#5F665F] font-mono">Type: {road.asset_type} &bull; Threat: {road.risk_level_at_asset}</span>
                  </div>
                  <span className="text-[10px] font-mono text-[#55758A] bg-[#FAF9F5] px-1.5 py-0.5 rounded border border-[#D5D2C8]">
                    {road.distance_meters?.toFixed(0) || 120} m away
                  </span>
                </div>
              ))
            ) : (
              <span className="text-[#889087] text-[11px]">No primary highways within immediate buffer.</span>
            )}
          </div>
        </div>

        {/* Nearby Settlements & Civil Facilities */}
        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
          <h4 className="font-bold text-xs text-[#20251F] mb-2 flex items-center gap-1.5 font-mono uppercase">
            <School className="w-3.5 h-3.5 text-[#806B52]" />
            Settlements & Institutional Exposure ({settlementAssets.length + criticalAssets.length})
          </h4>
          <div className="space-y-1.5">
            {[...settlementAssets, ...criticalAssets].length > 0 ? (
              [...settlementAssets, ...criticalAssets].map((asset: any, idx: number) => (
                <div key={idx} className="p-2 rounded bg-[#E9E6DD]/70 border border-[#D5D2C8] flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-[#20251F] block text-xs">{asset.name}</span>
                    <span className="text-[10px] text-[#5F665F] font-mono">
                      Type: {asset.asset_type} {asset.estimated_population_impact ? `&bull; Pop: ~${asset.estimated_population_impact}` : ''}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-[#806B52] bg-[#FAF9F5] px-1.5 py-0.5 rounded border border-[#D5D2C8]">
                    {asset.distance_meters?.toFixed(0) || 350} m away
                  </span>
                </div>
              ))
            ) : (
              <span className="text-[#889087] text-[11px]">No identified high-density settlements in buffer.</span>
            )}
          </div>
        </div>
      </div>

      {/* GIS Completeness Disclaimer */}
      <div className="p-2.5 rounded bg-[#FAF5EB] border border-[#E5D5B3] text-[10px] font-mono text-[#806B52] flex items-start gap-2">
        <ShieldAlert className="w-3.5 h-3.5 text-[#B18A3A] mt-0.5 flex-shrink-0" />
        <span>
          <strong>GIS Exposure Notice:</strong> {exposureData.completeness_warning ||
            'OpenStreetMap coverage in remote Northeast regions may be incomplete. Features represent buffer intersections and require on-ground district validation.'}
        </span>
      </div>
    </div>
  );
};
