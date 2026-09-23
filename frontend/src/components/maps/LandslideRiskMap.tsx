import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Polyline, Rectangle, Popup, useMap } from 'react-leaflet';
import {
  Filter,
  Search,
  MapPin,
  Grid,
  Navigation,
  Info,
  ShieldAlert,
} from 'lucide-react';
import { MapFeatureProperty } from '../../types';
import { api } from '../../services/api';
import { RiskBadge } from '../common/RiskBadge';
import { DataStatusBadge } from '../common/DataStatusBadge';

interface LandslideRiskMapProps {
  features: MapFeatureProperty[];
  selectedStationId: string | null;
  onSelectStation: (locationId: string) => void;
  onInspectStation: (locationId: string) => void;
}

const NER_STATES = [
  'All States',
  'Arunachal Pradesh',
  'Assam',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Sikkim',
  'Tripura',
];

const ChangeView: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  map.setView(center, zoom);
  return null;
};

export const LandslideRiskMap: React.FC<LandslideRiskMapProps> = ({
  features,
  selectedStationId,
  onSelectStation,
  onInspectStation,
}) => {
  const [selectedState, setSelectedState] = useState<string>('All States');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeLayer, setActiveLayer] = useState<'fused' | 'susceptibility' | 'dynamic' | 'rainfall'>('fused');
  const [activeStation, setActiveStation] = useState<MapFeatureProperty | null>(null);

  const [viewMode, setViewMode] = useState<'stations' | 'hotspots' | 'corridors'>('stations');
  const [hotspotCells, setHotspotCells] = useState<any[]>([]);
  const [corridors, setCorridors] = useState<any[]>([]);

  useEffect(() => {
    if (viewMode === 'hotspots') {
      api
        .getRegionalHotspots({ state: selectedState !== 'All States' ? selectedState : undefined })
        .then((res) => setHotspotCells(res.hotspots || []))
        .catch((err) => console.error('Failed to load regional hotspots', err));
    } else if (viewMode === 'corridors') {
      api
        .getTransportCorridors()
        .then((res) => setCorridors(res || []))
        .catch((err) => console.error('Failed to load transport corridors', err));
    }
  }, [viewMode, selectedState]);

  const filteredFeatures = features.filter((f) => {
    const matchesState = selectedState === 'All States' || f.state === selectedState;
    const matchesSearch =
      searchQuery === '' ||
      f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.district.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.state.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesState && matchesSearch;
  });

  const getMarkerColor = (f: MapFeatureProperty) => {
    if (activeLayer === 'susceptibility') {
      if (f.susceptibility_probability >= 0.8) return '#A83F3F';
      if (f.susceptibility_probability >= 0.6) return '#C96B3D';
      if (f.susceptibility_probability >= 0.39) return '#B18A3A';
      if (f.susceptibility_probability >= 0.2) return '#55758A';
      return '#5C7A61';
    } else if (activeLayer === 'dynamic') {
      if (f.dynamic_probability >= 0.5) return '#A83F3F';
      if (f.dynamic_probability >= 0.25) return '#C96B3D';
      if (f.dynamic_probability >= 0.1) return '#B18A3A';
      return '#5C7A61';
    } else if (activeLayer === 'rainfall') {
      if (f.rainfall_24h_mm >= 65.0) return '#A83F3F';
      if (f.rainfall_24h_mm >= 35.0) return '#C96B3D';
      if (f.rainfall_24h_mm >= 15.0) return '#55758A';
      return '#889087';
    } else {
      switch (f.final_risk) {
        case 'Critical':
          return '#A83F3F';
        case 'Alert':
          return '#C96B3D';
        case 'Watch':
          return '#B18A3A';
        case 'Normal':
        default:
          return '#5C7A61';
      }
    }
  };

  return (
    <div className="space-y-4">
      {/* Map Control Toolbar */}
      <div className="earth-panel p-3 flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex flex-wrap items-center gap-2">
          {/* State Filter */}
          <div className="flex items-center gap-1.5">
            <Filter className="w-3.5 h-3.5 text-[#5F665F]" />
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded px-2 py-1 focus:outline-none focus:border-[#496A52] font-mono"
            >
              {NER_STATES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2 top-1.5 text-[#889087]" />
            <input
              type="text"
              placeholder="Search station or district..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded pl-7 pr-2 py-1 focus:outline-none focus:border-[#496A52] w-40 sm:w-52"
            />
          </div>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-1 bg-[#E9E6DD] p-0.5 rounded border border-[#D5D2C8]">
          <button
            onClick={() => setViewMode('stations')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-mono font-medium transition-all ${
              viewMode === 'stations'
                ? 'bg-[#17201B] text-[#FAF9F5]'
                : 'text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            <MapPin className="w-3 h-3" />
            Stations ({filteredFeatures.length})
          </button>
          <button
            onClick={() => setViewMode('hotspots')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-mono font-medium transition-all ${
              viewMode === 'hotspots'
                ? 'bg-[#17201B] text-[#FAF9F5]'
                : 'text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            <Grid className="w-3 h-3" />
            Hotspot Grid
          </button>
          <button
            onClick={() => setViewMode('corridors')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-mono font-medium transition-all ${
              viewMode === 'corridors'
                ? 'bg-[#17201B] text-[#FAF9F5]'
                : 'text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            <Navigation className="w-3 h-3" />
            NH Corridors
          </button>
        </div>

        {/* Layer Switcher */}
        <div className="flex items-center gap-1 bg-[#E9E6DD] p-0.5 rounded border border-[#D5D2C8]">
          <button
            onClick={() => setActiveLayer('fused')}
            className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
              activeLayer === 'fused'
                ? 'bg-[#17201B] text-[#FAF9F5] font-semibold'
                : 'text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            Fused Risk
          </button>
          <button
            onClick={() => setActiveLayer('susceptibility')}
            className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
              activeLayer === 'susceptibility'
                ? 'bg-[#17201B] text-[#FAF9F5] font-semibold'
                : 'text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            Model 1 (Susc.)
          </button>
          <button
            onClick={() => setActiveLayer('dynamic')}
            className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
              activeLayer === 'dynamic'
                ? 'bg-[#17201B] text-[#FAF9F5] font-semibold'
                : 'text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            Model 2 (Dyn.)
          </button>
          <button
            onClick={() => setActiveLayer('rainfall')}
            className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
              activeLayer === 'rainfall'
                ? 'bg-[#17201B] text-[#FAF9F5] font-semibold'
                : 'text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            24h Rain
          </button>
        </div>
      </div>

      {/* Main Map Container */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3 rounded border border-[#D5D2C8] h-[620px] relative shadow-sm overflow-hidden">
          <MapContainer
            center={[26.2006, 92.9376]}
            zoom={7}
            scrollWheelZoom={true}
            style={{ height: '100%', width: '100%' }}
          >
            <ChangeView center={[26.2006, 92.9376]} zoom={7} />
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* 1. Monitoring Station Circle Markers */}
            {viewMode === 'stations' &&
              filteredFeatures.map((feature) => {
                const color = getMarkerColor(feature);
                const isSelected = selectedStationId === feature.location_id;
                return (
                  <CircleMarker
                    key={feature.location_id}
                    center={[
                      feature.elevation_m !== undefined ? (feature as any).latitude || 26.2 : 26.2,
                      feature.slope_deg !== undefined ? (feature as any).longitude || 92.9 : 92.9,
                    ]}
                    radius={isSelected ? 9 : 6.5}
                    pathOptions={{
                      color: isSelected ? '#17201B' : color,
                      fillColor: color,
                      fillOpacity: 0.92,
                      weight: isSelected ? 2.5 : 1.5,
                    }}
                    eventHandlers={{
                      click: () => {
                        setActiveStation(feature);
                        onSelectStation(feature.location_id);
                      },
                    }}
                  >
                    <Popup>
                      <div className="p-1 space-y-2 text-[#20251F] font-sans">
                        <div className="flex items-center justify-between gap-2 border-b border-[#D5D2C8] pb-1.5">
                          <span className="font-bold text-xs text-[#20251F]">{feature.name}</span>
                          <RiskBadge level={feature.final_risk} size="sm" />
                        </div>
                        <div className="text-[11px] text-[#5F665F]">
                          {feature.district}, {feature.state}
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-[10px] font-mono bg-[#E9E6DD] p-2 rounded border border-[#D5D2C8]">
                          <div>
                            <span className="text-[#5F665F] block">Model 1 (Susc):</span>
                            <span className="font-semibold text-[#20251F]">
                              {(feature.susceptibility_probability * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div>
                            <span className="text-[#5F665F] block">Model 2 (Dyn):</span>
                            <span className="font-semibold text-[#20251F]">
                              {(feature.dynamic_probability * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div>
                            <span className="text-[#5F665F] block">24h Rain:</span>
                            <span className="font-semibold text-[#55758A]">
                              {feature.rainfall_24h_mm.toFixed(1)} mm
                            </span>
                          </div>
                          <div>
                            <span className="text-[#5F665F] block">Fused Threat:</span>
                            <span className="font-semibold text-[#B18A3A]">
                              {(feature.combined_risk_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => onInspectStation(feature.location_id)}
                          className="w-full mt-2 py-1 bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] rounded font-semibold text-xs transition-colors font-mono"
                        >
                          Inspect Telemetry
                        </button>
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}

            {/* 2. Regional Hotspots Grid Layer */}
            {viewMode === 'hotspots' &&
              hotspotCells.map((cell) => {
                const cellColor =
                  cell.risk_level === 'Critical'
                    ? '#A83F3F'
                    : cell.risk_level === 'Alert'
                    ? '#C96B3D'
                    : cell.risk_level === 'Watch'
                    ? '#B18A3A'
                    : '#5C7A61';
                return (
                  <Rectangle
                    key={cell.cell_id}
                    bounds={[
                      [cell.min_lat, cell.min_lon],
                      [cell.max_lat, cell.max_lon],
                    ]}
                    pathOptions={{
                      color: cellColor,
                      fillColor: cellColor,
                      fillOpacity: 0.45,
                      weight: 1,
                    }}
                  >
                    <Popup>
                      <div className="p-1 space-y-1.5 text-xs text-[#20251F] font-sans">
                        <div className="flex items-center justify-between border-b border-[#D5D2C8] pb-1">
                          <strong className="text-[#20251F]">Grid Cell {cell.cell_id}</strong>
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#FAF5EB] text-[#B18A3A] font-mono border border-[#E5D5B3]">
                            {cell.risk_level}
                          </span>
                        </div>
                        <div className="text-[11px] text-[#5F665F]">
                          {cell.district}, {cell.state}
                        </div>
                        <div className="text-[10px] font-mono text-[#20251F]">
                          <div>Susc Prob: {(cell.susceptibility_probability * 100).toFixed(1)}%</div>
                          <div>Rain Index: {(cell.rainfall_trigger_score * 100).toFixed(0)}%</div>
                          <div>Fused Threat: {(cell.fused_risk_score * 100).toFixed(1)}%</div>
                        </div>
                      </div>
                    </Popup>
                  </Rectangle>
                );
              })}

            {/* 3. National Highway Lifeline Corridors */}
            {viewMode === 'corridors' &&
              corridors
                .filter((c) => Array.isArray(c.polyline_coordinates) && c.polyline_coordinates.length >= 2)
                .map((c) => {
                  // Ensure coordinates are [lat, lon] for Leaflet
                  const validPositions: [number, number][] = c.polyline_coordinates.map((pt: any) => {
                    if (Array.isArray(pt) && pt.length >= 2) {
                      // Check if pt is [lon, lat] where lon > 80 and lat < 40
                      if (pt[0] > 70 && pt[1] < 40) {
                        return [pt[1], pt[0]]; // Flip to [lat, lon]
                      }
                      return [pt[0], pt[1]];
                    }
                    return [26.0, 92.0];
                  });

                  const isHighRisk = c.risk_level === 'Critical' || c.risk_level === 'Alert' || (c.high_risk_segments_count && c.high_risk_segments_count > 0);
                  const lineColor = c.risk_level === 'Critical' ? '#A83F3F' : c.risk_level === 'Alert' ? '#C96B3D' : '#55758A';

                  return (
                    <Polyline
                      key={c.corridor_id}
                      positions={validPositions}
                      pathOptions={{
                        color: lineColor,
                        weight: 4.5,
                        dashArray: isHighRisk ? '6, 6' : undefined,
                      }}
                    >
                      <Popup>
                        <div className="p-1 space-y-1.5 text-xs text-[#20251F]">
                          <strong className="text-[#20251F] block text-xs">{c.corridor_name}</strong>
                          <div className="text-[11px] text-[#5F665F]">
                            Length: {c.total_length_km || c.length_km || 100} km &bull; {c.state_corridor || c.state || 'NER Arterial'}
                          </div>
                          {c.known_chokepoints && Array.isArray(c.known_chokepoints) && c.known_chokepoints.length > 0 && (
                            <div className="text-[10px] font-mono text-[#806B52] bg-[#E9E6DD]/60 p-1 rounded border border-[#D5D2C8]">
                              <span className="font-bold block">Key Chokepoints:</span>
                              {c.known_chokepoints.slice(0, 3).join(', ')}
                            </div>
                          )}
                          <div className="text-[11px] text-[#B18A3A] font-mono">
                            High Risk Segments: {c.high_risk_segments_count ?? 1} of {c.total_segments ?? 4}
                          </div>
                        </div>
                      </Popup>
                    </Polyline>
                  );
                })}
          </MapContainer>

          {/* Floating Map Legend */}
          <div className="absolute bottom-3 left-3 z-[1000] bg-[#FAF9F5]/95 backdrop-blur-xs p-2.5 rounded border border-[#D5D2C8] text-xs shadow pointer-events-auto max-w-xs font-mono">
            <div className="font-bold text-[#20251F] mb-1.5 flex items-center justify-between text-[11px]">
              <span>LAYER: {activeLayer.toUpperCase()}</span>
              <Info className="w-3.5 h-3.5 text-[#5F665F]" />
            </div>

            {activeLayer === 'fused' && (
              <div className="space-y-1 text-[10px]">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#A83F3F]" />
                  <span className="text-[#20251F]">Critical (Score ≥ 0.75)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#C96B3D]" />
                  <span className="text-[#20251F]">Alert (Score ≥ 0.50)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#B18A3A]" />
                  <span className="text-[#20251F]">Watch (Score ≥ 0.25)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#5C7A61]" />
                  <span className="text-[#20251F]">Normal Baseline (&lt; 0.25)</span>
                </div>
              </div>
            )}

            {activeLayer === 'susceptibility' && (
              <div className="space-y-1 text-[10px]">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#A83F3F]" />
                  <span className="text-[#20251F]">Very High (≥ 80%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#C96B3D]" />
                  <span className="text-[#20251F]">High (≥ 60%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#B18A3A]" />
                  <span className="text-[#20251F]">Moderate (Threshold 39%)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#5C7A61]" />
                  <span className="text-[#20251F]">Low / Very Low (&lt; 39%)</span>
                </div>
              </div>
            )}

            {activeLayer === 'rainfall' && (
              <div className="space-y-1 text-[10px]">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#A83F3F]" />
                  <span className="text-[#20251F]">Critical Rain (≥ 65mm)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#C96B3D]" />
                  <span className="text-[#20251F]">High Rain (≥ 35mm)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#55758A]" />
                  <span className="text-[#20251F]">Elevated Rain (≥ 15mm)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#889087]" />
                  <span className="text-[#20251F]">Low Rain (&lt; 15mm)</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Side Panel: Selected Station Inspector */}
        <div className="earth-panel p-3.5 flex flex-col justify-between h-[620px] overflow-y-auto">
          {activeStation ? (
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-sm text-[#20251F]">{activeStation.name}</h3>
                  <p className="text-[11px] text-[#5F665F] font-mono">
                    {activeStation.district}, {activeStation.state}
                  </p>
                </div>
                <RiskBadge level={activeStation.final_risk} size="md" />
              </div>

              <div className="flex items-center justify-between">
                <DataStatusBadge
                  status={activeStation.data_status}
                  ageHours={activeStation.data_age_hours}
                />
                <span className="text-[10px] font-mono text-[#5F665F]">
                  Elev: {activeStation.elevation_m || 450}m
                </span>
              </div>

              {/* Threat Matrix Breakdown */}
              <div className="space-y-2 pt-1">
                <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
                  <div className="flex items-center justify-between text-xs text-[#5F665F] mb-1 font-mono">
                    <span>Model 1 Susc. (45%)</span>
                    <span className="font-bold text-[#20251F]">
                      {(activeStation.susceptibility_probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-[#E9E6DD] h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-[#B18A3A] h-full rounded-full"
                      style={{ width: `${Math.min(100, activeStation.susceptibility_probability * 100)}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-[#889087] mt-1 block font-mono">
                    Class: {activeStation.susceptibility_class} (Thresh: 0.39)
                  </span>
                </div>

                <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
                  <div className="flex items-center justify-between text-xs text-[#5F665F] mb-1 font-mono">
                    <span>Model 2 Early Warning (55%)</span>
                    <span className="font-bold text-[#20251F]">
                      {(activeStation.dynamic_probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-[#E9E6DD] h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-[#55758A] h-full rounded-full"
                      style={{ width: `${Math.min(100, activeStation.dynamic_probability * 100)}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-[#889087] mt-1 block font-mono">
                    Candidate: {activeStation.warning_candidate ? 'Triggered (≥0.10)' : 'Below Threshold'}
                  </span>
                </div>

                <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
                  <div className="flex items-center justify-between text-xs text-[#5F665F] mb-1 font-mono">
                    <span>24h Rain Intensity</span>
                    <span className="font-bold text-[#55758A]">{activeStation.rainfall_24h_mm.toFixed(1)} mm</span>
                  </div>
                  <span className="text-[10px] text-[#889087] block font-mono">
                    Band: {activeStation.rainfall_class}
                  </span>
                </div>
              </div>

              <div className="p-2.5 rounded bg-[#FAF5EB] border border-[#E5D5B3] text-[10px] font-mono text-[#806B52]">
                <ShieldAlert className="w-3.5 h-3.5 inline mr-1 text-[#B18A3A]" />
                Deterministic research score clipped to [0, 1].
              </div>

              <button
                onClick={() => onInspectStation(activeStation.location_id)}
                className="w-full py-2 bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] font-bold rounded text-xs transition-colors font-mono"
              >
                Inspect Telemetry Console
              </button>
            </div>
          ) : viewMode === 'corridors' ? (
            <div className="space-y-3">
              <div className="border-b border-[#D5D2C8] pb-2">
                <h4 className="font-bold text-xs text-[#20251F] uppercase font-mono flex items-center gap-1.5">
                  <Navigation className="w-3.5 h-3.5 text-[#496A52]" />
                  National Highway Lifelines ({corridors.length})
                </h4>
                <p className="text-[11px] text-[#5F665F]">
                  Strategic transport arteries monitored for landslide blockages & chokepoints.
                </p>
              </div>

              <div className="space-y-2 max-h-[460px] overflow-y-auto pr-1">
                {corridors.map((c) => (
                  <div
                    key={c.corridor_id}
                    className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8] hover:border-[#806B52] transition-colors"
                  >
                    <div className="flex items-start justify-between gap-1 mb-1">
                      <span className="font-bold text-xs text-[#20251F]">{c.corridor_name}</span>
                      <RiskBadge level={c.risk_level || 'Watch'} size="sm" />
                    </div>
                    <div className="text-[11px] text-[#5F665F] font-mono mb-1">
                      {c.state_corridor || c.state} &bull; {c.total_length_km || c.length_km} km
                    </div>
                    {c.known_chokepoints && Array.isArray(c.known_chokepoints) && c.known_chokepoints.length > 0 && (
                      <div className="text-[10px] text-[#806B52] font-mono bg-[#E9E6DD]/60 p-1 rounded border border-[#D5D2C8]">
                        <span className="font-bold block text-[9px] uppercase">Chokepoints:</span>
                        {c.known_chokepoints.slice(0, 2).join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center text-[#889087] p-4">
              <MapPin className="w-7 h-7 mb-2 text-[#C4BFB2]" />
              <h4 className="font-semibold text-[#20251F] text-xs">No Station Selected</h4>
              <p className="text-[11px] text-[#5F665F] mt-1">
                Click any marker on the map to inspect its real-time AI susceptibility and dynamic early warning indicators.
              </p>
            </div>
          )}

          <div className="text-[10px] font-mono text-[#889087] pt-2 border-t border-[#E2DFD5]">
            Showing {filteredFeatures.length} of {features.length} NER stations
          </div>
        </div>
      </div>
    </div>
  );
};
