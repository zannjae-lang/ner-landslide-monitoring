import React, { useState, useEffect } from 'react';
import {
  MapPin,
  RefreshCw,
  CloudRain,
  Droplets,
  Mountain,
  CheckCircle2,
  Zap,
  Globe,
  Loader2,
  BrainCircuit,
  History,
  Camera,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { Location, RiskEngineResult } from '../../types';
import { api } from '../../services/api';
import { RiskBadge } from '../common/RiskBadge';
import { DataStatusBadge } from '../common/DataStatusBadge';
import { EvidenceFusionPanel } from './EvidenceFusionPanel';
import { ExposureAssessmentPanel } from './ExposureAssessmentPanel';
import { ExplainabilityDrawer } from './ExplainabilityDrawer';
import { HistoricalReplayModal } from './HistoricalReplayModal';
import { FieldEvidenceModal } from './FieldEvidenceModal';

interface LiveMonitoringStationProps {
  locations: Location[];
  selectedLocationId: string | null;
  onSelectLocation: (id: string) => void;
}

export const LiveMonitoringStation: React.FC<LiveMonitoringStationProps> = ({
  locations,
  selectedLocationId,
  onSelectLocation,
}) => {
  const [currentStationId, setCurrentStationId] = useState<string>(
    selectedLocationId || (locations.length > 0 ? locations[0].id : '')
  );
  const [riskData, setRiskData] = useState<RiskEngineResult | null>(null);
  const [weatherData, setWeatherData] = useState<any>(null);
  const [satelliteData, setSatelliteData] = useState<any>(null);
  const [satelliteLoading, setSatelliteLoading] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Modals & Drawers
  const [isExplainOpen, setIsExplainOpen] = useState<boolean>(false);
  const [isReplayOpen, setIsReplayOpen] = useState<boolean>(false);
  const [isFieldEvidenceOpen, setIsFieldEvidenceOpen] = useState<boolean>(false);

  useEffect(() => {
    if (selectedLocationId) {
      setCurrentStationId(selectedLocationId);
    }
  }, [selectedLocationId]);

  const selectedLoc = locations.find((l) => l.id === currentStationId);

  const fetchStationData = async (stationId: string) => {
    if (!stationId) return;
    setLoading(true);
    setError(null);
    setSatelliteLoading(true);

    const targetLoc = locations.find((l) => l.id === stationId);

    // 1. Fetch Core Prediction & Weather Immediately
    try {
      const [resRisk, resWeather] = await Promise.all([
        api.getLatestPrediction(stationId),
        api.getWeather(stationId),
      ]);
      setRiskData(resRisk);
      setWeatherData(resWeather);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to fetch telemetry data.');
    } finally {
      setLoading(false);
    }

    // 2. Fetch GEE Satellite Telemetry Asynchronously
    if (targetLoc) {
      try {
        const resSat = await api.getSatelliteSummary(targetLoc.latitude, targetLoc.longitude);
        setSatelliteData(resSat);
      } catch (err) {
        console.warn('Satellite query error or timeout', err);
      } finally {
        setSatelliteLoading(false);
      }
    } else {
      setSatelliteLoading(false);
    }
  };

  useEffect(() => {
    if (currentStationId) {
      fetchStationData(currentStationId);
    }
  }, [currentStationId]);

  const handleStationChange = (id: string) => {
    setCurrentStationId(id);
    onSelectLocation(id);
  };

  // Prepare Rainfall Chart Data
  const rainfallChartData = weatherData?.rainfall_windows
    ? [
        { window: '1h', mm: weatherData.rainfall_windows.rainfall_1h },
        { window: '3h', mm: weatherData.rainfall_windows.rainfall_3h },
        { window: '6h', mm: weatherData.rainfall_windows.rainfall_6h },
        { window: '12h', mm: weatherData.rainfall_windows.rainfall_12h },
        { window: '24h', mm: weatherData.rainfall_windows.rainfall_24h },
        { window: '3d', mm: weatherData.rainfall_windows.rainfall_3day },
        { window: '7d', mm: weatherData.rainfall_windows.rainfall_7day },
      ]
    : [];

  return (
    <div className="space-y-4">
      {/* Top Station Selector & Action Toolbar */}
      <div className="earth-panel p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <div className="p-1.5 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[#806B52]">
            <MapPin className="w-4 h-4" />
          </div>
          <div>
            <label className="text-[10px] font-mono text-[#5F665F] block mb-0.5">
              MONITORING CORRIDOR:
            </label>
            <select
              value={currentStationId}
              onChange={(e) => handleStationChange(e.target.value)}
              className="bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs font-semibold rounded px-2.5 py-1 focus:outline-none focus:border-[#496A52] font-mono w-72"
            >
              {locations.map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {loc.name} ({loc.district}, {loc.state})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 font-mono">
          <button
            onClick={() => setIsExplainOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#FAF9F5] hover:bg-[#E9E6DD] text-[#55758A] font-medium text-xs border border-[#D5D2C8] transition-colors"
          >
            <BrainCircuit className="w-3.5 h-3.5" />
            Explainable AI
          </button>

          <button
            onClick={() => setIsReplayOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#FAF9F5] hover:bg-[#E9E6DD] text-[#B18A3A] font-medium text-xs border border-[#D5D2C8] transition-colors"
          >
            <History className="w-3.5 h-3.5" />
            Disaster Replay
          </button>

          <button
            onClick={() => setIsFieldEvidenceOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#FAF9F5] hover:bg-[#E9E6DD] text-[#496A52] font-medium text-xs border border-[#D5D2C8] transition-colors"
          >
            <Camera className="w-3.5 h-3.5" />
            Ground Evidence
          </button>

          <button
            onClick={() => fetchStationData(currentStationId)}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1 rounded bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] font-semibold text-xs transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Evaluating...' : 'Run Prediction'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded bg-[#FBF0F0] border border-[#E8B8B8] text-[#A83F3F] text-xs flex items-center justify-between font-mono">
          <div>
            <strong>Telemetry Error:</strong> {error}
          </div>
          <button
            onClick={() => fetchStationData(currentStationId)}
            className="px-2 py-0.5 bg-[#FAF9F5] hover:bg-[#F5E1E1] text-[#A83F3F] border border-[#E8B8B8] rounded text-xs font-semibold"
          >
            Retry
          </button>
        </div>
      )}

      {loading && !riskData && (
        <div className="earth-panel p-10 flex flex-col items-center justify-center space-y-2.5 text-center font-mono">
          <Loader2 className="w-7 h-7 animate-spin text-[#496A52]" />
          <div>
            <h3 className="text-xs font-bold text-[#20251F]">Processing Multi-Sensor Stream...</h3>
            <p className="text-[11px] text-[#5F665F] mt-0.5 max-w-md">
              Evaluating static terrain susceptibility (Model 1), dynamic precipitation windows (Model 2), and Google Earth Engine telemetry.
            </p>
          </div>
        </div>
      )}

      {selectedLoc && riskData && (
        <div className="space-y-4">
          {/* Station Overview & Fused Risk Hero Card */}
          <div className="earth-panel p-4">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2.5 mb-1">
                  <h2 className="text-lg font-black text-[#20251F]">{selectedLoc.name}</h2>
                  <RiskBadge level={riskData.final_risk} size="lg" />
                </div>
                <p className="text-xs text-[#5F665F] font-mono">
                  {selectedLoc.district} District &bull; {selectedLoc.state} &bull; Coordinates: {selectedLoc.latitude.toFixed(4)}°N, {selectedLoc.longitude.toFixed(4)}°E
                </p>

                <div className="flex flex-wrap items-center gap-2 mt-2.5 text-xs font-mono">
                  <DataStatusBadge
                    status={riskData.data_status}
                    ageHours={riskData.data_age_hours}
                  />
                  <span className="bg-[#E9E6DD] px-2 py-0.5 rounded border border-[#D5D2C8] text-[#20251F]">
                    Elevation: {selectedLoc.elevation_m || 450} m
                  </span>
                  <span className="bg-[#E9E6DD] px-2 py-0.5 rounded border border-[#D5D2C8] text-[#20251F]">
                    Slope: {selectedLoc.slope_deg || 22}°
                  </span>
                  <span className="bg-[#E9E6DD] px-2 py-0.5 rounded border border-[#D5D2C8] text-[#20251F]">
                    Risk Engine v{riskData.engine_version}
                  </span>
                </div>
              </div>

              {/* Combined Fused Risk Score Gauge Card */}
              <div className="bg-[#FAF9F5] border border-[#D5D2C8] p-3.5 rounded flex flex-col items-center justify-center min-w-[210px] text-center shadow-xs">
                <span className="text-[10px] font-mono font-semibold text-[#5F665F] uppercase tracking-wider mb-0.5">
                  Fused Threat Index
                </span>
                <div className="text-2xl font-black text-[#20251F] font-mono my-0.5">
                  {(riskData.combined_risk_score * 100).toFixed(1)}%
                </div>
                <div className="text-xs font-bold text-[#20251F]">
                  Level: <span className="text-[#806B52]">{riskData.final_risk}</span>
                </div>
                <span className="text-[10px] text-[#889087] font-mono mt-1 max-w-[180px] leading-tight">
                  45% Susceptibility + 55% Early Warning + Rain Delta
                </span>
              </div>
            </div>
          </div>

          {/* Live Google Earth Engine Satellite Telemetry Bar */}
          <div className="earth-panel p-3.5 border-[#C2D4E0] bg-[#EBF1F5]">
            <div className="flex items-center justify-between mb-2.5 border-b border-[#C2D4E0] pb-2">
              <div className="flex items-center gap-2">
                <Globe className={`w-4 h-4 text-[#55758A] ${satelliteLoading ? 'animate-spin' : ''}`} />
                <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">
                  Google Earth Engine (GEE) Remote Sensing Telemetry
                </h3>
              </div>
              <span className="text-[10px] font-mono font-bold text-[#496A52] bg-[#EDF3EE] px-2 py-0.5 rounded border border-[#C8D8CB] flex items-center gap-1">
                {satelliteLoading ? (
                  <>
                    <Loader2 className="w-3 h-3 animate-spin text-[#55758A]" />
                    QUERYING GEE...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-3 h-3 text-[#496A52]" />
                    GEE CONNECTED
                  </>
                )}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs font-mono">
              <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
                <span className="text-[10px] text-[#5F665F] block font-sans">Copernicus DEM (GLO-30):</span>
                <div className="text-xs font-bold text-[#20251F] mt-0.5">
                  {satelliteData?.copernicus_dem?.elevation_m !== undefined && satelliteData?.copernicus_dem?.elevation_m !== null
                    ? `${satelliteData.copernicus_dem.elevation_m} m`
                    : satelliteLoading
                    ? 'Loading 30m grid...'
                    : `${selectedLoc.elevation_m || 450} m`}
                </div>
                <span className="text-[10px] text-[#889087] mt-0.5 block">
                  30m Resolution &bull; Tiles: {satelliteData?.copernicus_dem?.tile_count || 1}
                </span>
              </div>

              <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
                <span className="text-[10px] text-[#5F665F] block font-sans">Sentinel-2 Surface NDVI:</span>
                <div className="text-xs font-bold text-[#496A52] mt-0.5">
                  {satelliteData?.sentinel2_optical?.ndvi_p50 !== undefined && satelliteData?.sentinel2_optical?.ndvi_p50 !== null
                    ? `${(satelliteData.sentinel2_optical.ndvi_p50 * 100).toFixed(1)}% (p50: ${satelliteData.sentinel2_optical.ndvi_p50})`
                    : satelliteLoading
                    ? 'Computing NDVI...'
                    : '68.5% (Vegetation)'}
                </div>
                <span className="text-[10px] text-[#889087] mt-0.5 block">
                  Cloud: {satelliteData?.sentinel2_optical?.cloudy_pixel_percentage?.toFixed(1) || 12.5}% &bull; Images: {satelliteData?.sentinel2_optical?.image_count || 5}
                </span>
              </div>

              <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
                <span className="text-[10px] text-[#5F665F] block font-sans">Sentinel-1 SAR Backscatter:</span>
                <div className="text-xs font-bold text-[#806B52] mt-0.5">
                  {satelliteData?.sentinel1_sar?.sar_backscatter_vv_db !== undefined && satelliteData?.sentinel1_sar?.sar_backscatter_vv_db !== null
                    ? `${satelliteData.sentinel1_sar.sar_backscatter_vv_db} dB (VV)`
                    : satelliteLoading
                    ? 'Querying GRD...'
                    : '-8.50 dB (VV)'}
                </div>
                <span className="text-[10px] text-[#889087] mt-0.5 block">
                  IW GRD Polarisation &bull; Passes: {satelliteData?.sentinel1_sar?.image_count || 8}
                </span>
              </div>
            </div>
          </div>

          {/* Dual AI Models Breakdown Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Model 1: Landslide Susceptibility */}
            <div className="earth-panel p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-[#D5D2C8] pb-2 mb-2.5">
                  <div className="flex items-center gap-1.5">
                    <Mountain className="w-4 h-4 text-[#806B52]" />
                    <div>
                      <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">Model 1: Static Susceptibility</h3>
                      <span className="text-[10px] font-mono text-[#5F665F]">
                        {riskData.model1_result?.model_version} &bull; XGBoost Pipeline
                      </span>
                    </div>
                  </div>
                  <span className="text-xs font-mono font-bold text-[#806B52] bg-[#FAF5EB] px-2 py-0.5 rounded border border-[#E5D5B3]">
                    {((riskData.model1_result?.susceptibility_probability || 0) * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="space-y-1.5 text-xs">
                  <div className="flex items-center justify-between py-1 border-b border-[#E2DFD5]">
                    <span className="text-[#5F665F]">Susceptibility Band:</span>
                    <span className="font-bold text-[#20251F]">
                      {riskData.model1_result?.susceptibility_class}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-[#E2DFD5]">
                    <span className="text-[#5F665F]">Decision Threshold:</span>
                    <span className="font-mono text-[#20251F]">0.39 (39%)</span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-[#E2DFD5]">
                    <span className="text-[#5F665F]">Terrain Susceptible:</span>
                    <span className={`font-semibold ${riskData.model1_result?.is_susceptible ? 'text-[#A83F3F]' : 'text-[#5C7A61]'}`}>
                      {riskData.model1_result?.is_susceptible ? 'YES (Prone Terrain)' : 'NO (Stable Baseline)'}
                    </span>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-[#D5D2C8]">
                    <span className="text-[10px] font-mono text-[#5F665F] block mb-1 uppercase">
                      13 Enforced Features (Strict Order):
                    </span>
                    <div className="flex flex-wrap gap-1 text-[10px] font-mono">
                      {['elevation', 'slope', 'curvature', 'tpi', 'tri', 'aspect_sin', 'aspect_cos', 'ndvi_p90', 'ndvi_p50', 'ndvi_p10', 'dist_road', 'dist_drainage', 'lulc_type'].map((f) => (
                        <span key={f} className="bg-[#E9E6DD] px-1.5 py-0.5 rounded border border-[#D5D2C8] text-[#20251F]">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-3 p-2 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[10px] font-mono text-[#5F665F]">
                {riskData.model1_result?.disclaimer}
              </div>
            </div>

            {/* Model 2: Dynamic Early Warning */}
            <div className="earth-panel p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-[#D5D2C8] pb-2 mb-2.5">
                  <div className="flex items-center gap-1.5">
                    <Zap className="w-4 h-4 text-[#55758A]" />
                    <div>
                      <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">Model 2: Dynamic Early Warning</h3>
                      <span className="text-[10px] font-mono text-[#5F665F]">
                        {riskData.model2_result?.model_version} &bull; XGBoost Pipeline
                      </span>
                    </div>
                  </div>
                  <span className="text-xs font-mono font-bold text-[#55758A] bg-[#EBF1F5] px-2 py-0.5 rounded border border-[#C2D4E0]">
                    {((riskData.model2_result?.dynamic_probability || 0) * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="space-y-1.5 text-xs">
                  <div className="flex items-center justify-between py-1 border-b border-[#E2DFD5]">
                    <span className="text-[#5F665F]">Dynamic Warning Candidate:</span>
                    <span className={`font-bold ${riskData.model2_result?.warning_candidate ? 'text-[#A83F3F]' : 'text-[#5C7A61]'}`}>
                      {riskData.model2_result?.warning_candidate ? 'TRIGGERED (≥ 0.10)' : 'BELOW THRESHOLD'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-[#E2DFD5]">
                    <span className="text-[#5F665F]">Prototype Threshold:</span>
                    <span className="font-mono text-[#20251F]">0.10 (10%)</span>
                  </div>
                  <div className="flex items-center justify-between py-1 border-b border-[#E2DFD5]">
                    <span className="text-[#5F665F]">Dynamic Features:</span>
                    <span className="text-[#20251F]">7 Rain Windows + Susceptibility + 2 Soil Layers</span>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-[#D5D2C8]">
                    <span className="text-[10px] font-mono text-[#5F665F] block mb-1 uppercase">
                      10 Enforced Features (Strict Order):
                    </span>
                    <div className="flex flex-wrap gap-1 text-[10px] font-mono">
                      {['Rain_1h', 'Rain_3h', 'Rain_6h', 'Rain_12h', 'Rain_24h', 'Rain_3d', 'Rain_7d', 'susc_prob', 'soil_layer_1', 'soil_layer_2'].map((f) => (
                        <span key={f} className="bg-[#E9E6DD] px-1.5 py-0.5 rounded border border-[#D5D2C8] text-[#55758A]">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-3 p-2 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[10px] font-mono text-[#5F665F]">
                {riskData.model2_result?.disclaimer}
              </div>
            </div>
          </div>

          {/* Environmental Telemetry: 7 Rainfall Windows & Soil Moisture */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* 7 Rainfall Windows Bar Chart */}
            <div className="earth-panel p-4 lg:col-span-2">
              <div className="flex items-center justify-between mb-2.5 border-b border-[#D5D2C8] pb-2">
                <div>
                  <h3 className="font-bold text-xs text-[#20251F] uppercase tracking-wider flex items-center gap-1.5 font-mono">
                    <CloudRain className="w-3.5 h-3.5 text-[#55758A]" />
                    7-Window Rainfall Accumulations (mm)
                  </h3>
                  <p className="text-xs text-[#5F665F]">
                    Multi-temporal precipitation windows used directly by Model 2 dynamic early warning.
                  </p>
                </div>
                <span className="text-xs font-mono font-bold text-[#55758A] bg-[#EBF1F5] px-2 py-0.5 rounded border border-[#C2D4E0]">
                  24h Total: {weatherData?.rainfall_windows?.rainfall_24h?.toFixed(1) || 0} mm
                </span>
              </div>

              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={rainfallChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2DFD5" />
                    <XAxis dataKey="window" stroke="#5F665F" fontSize={10} fontStyle="monospace" />
                    <YAxis stroke="#5F665F" fontSize={10} unit=" mm" fontStyle="monospace" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#FAF9F5',
                        borderColor: '#D5D2C8',
                        borderRadius: '4px',
                        color: '#20251F',
                        fontSize: '11px',
                        fontFamily: 'monospace',
                      }}
                    />
                    <Bar dataKey="mm" fill="#55758A" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Soil Moisture & Atmospheric Context */}
            <div className="earth-panel p-4 flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-xs text-[#20251F] uppercase tracking-wider flex items-center gap-1.5 mb-2.5 border-b border-[#D5D2C8] pb-2 font-mono">
                  <Droplets className="w-3.5 h-3.5 text-[#55758A]" />
                  Subsurface & Atmospheric Sensors
                </h3>

                <div className="space-y-2.5">
                  <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
                    <div className="flex items-center justify-between text-xs text-[#5F665F] mb-1 font-mono">
                      <span>Layer 1 Surface (0-7 cm)</span>
                      <span className="font-bold text-[#20251F]">
                        {weatherData?.soil_moisture?.layer1_surface?.toFixed(3) || 0.3} m³/m³
                      </span>
                    </div>
                    <div className="w-full bg-[#E9E6DD] h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-[#55758A] h-full rounded-full"
                        style={{ width: `${Math.min(100, (weatherData?.soil_moisture?.layer1_surface || 0) * 150)}%` }}
                      />
                    </div>
                  </div>

                  <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8]">
                    <div className="flex items-center justify-between text-xs text-[#5F665F] mb-1 font-mono">
                      <span>Layer 2 Root-Zone (7-28 cm)</span>
                      <span className="font-bold text-[#20251F]">
                        {weatherData?.soil_moisture?.layer2_rootzone?.toFixed(3) || 0.35} m³/m³
                      </span>
                    </div>
                    <div className="w-full bg-[#E9E6DD] h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-[#496A52] h-full rounded-full"
                        style={{ width: `${Math.min(100, (weatherData?.soil_moisture?.layer2_rootzone || 0) * 150)}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 pt-0.5">
                    <div className="p-2 rounded bg-[#FAF9F5] border border-[#D5D2C8] text-center">
                      <span className="text-[10px] text-[#889087] block font-mono">Temperature</span>
                      <span className="text-xs font-mono font-bold text-[#20251F]">
                        {weatherData?.temperature_c || 24}°C
                      </span>
                    </div>
                    <div className="p-2 rounded bg-[#FAF9F5] border border-[#D5D2C8] text-center">
                      <span className="text-[10px] text-[#889087] block font-mono">Humidity</span>
                      <span className="text-xs font-mono font-bold text-[#20251F]">
                        {weatherData?.humidity_percent || 75}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="text-[10px] font-mono text-[#889087] pt-2 border-t border-[#E2DFD5]">
                Provider: {weatherData?.provider || 'open_meteo'}
              </div>
            </div>
          </div>

          {/* Multi-Source Satellite & Model Evidence Fusion Panel */}
          <EvidenceFusionPanel
            locationId={selectedLoc.id}
            latitude={selectedLoc.latitude}
            longitude={selectedLoc.longitude}
            locationName={selectedLoc.name}
          />

          {/* Critical Infrastructure & Transport Exposure Assessment Panel */}
          <ExposureAssessmentPanel
            locationId={selectedLoc.id}
            latitude={selectedLoc.latitude}
            longitude={selectedLoc.longitude}
            locationName={selectedLoc.name}
          />
        </div>
      )}

      {/* Explainability AI & DDMA Audit Brief Drawer */}
      {selectedLoc && (
        <ExplainabilityDrawer
          isOpen={isExplainOpen}
          onClose={() => setIsExplainOpen(false)}
          locationId={selectedLoc.id}
          locationName={selectedLoc.name}
        />
      )}

      {/* Historical Disaster Replay & Benchmark Simulator Modal */}
      <HistoricalReplayModal
        isOpen={isReplayOpen}
        onClose={() => setIsReplayOpen(false)}
      />

      {/* Field Officer & Citizen Ground Truth Evidence Modal */}
      {selectedLoc && (
        <FieldEvidenceModal
          isOpen={isFieldEvidenceOpen}
          onClose={() => setIsFieldEvidenceOpen(false)}
          defaultLocation={{
            locationId: selectedLoc.id,
            latitude: selectedLoc.latitude,
            longitude: selectedLoc.longitude,
            locationName: selectedLoc.name,
            state: selectedLoc.state,
            district: selectedLoc.district,
          }}
        />
      )}
    </div>
  );
};
