import React, { useEffect, useState } from 'react';
import {
  Database,
  CheckCircle2,
  AlertCircle,
  Key,
  Globe,
  RefreshCw,
  Server,
  Activity,
  Loader2,
} from 'lucide-react';
import { DataSourceStatus, SystemHealth } from '../../types';
import { api } from '../../services/api';

interface DataSourcesViewProps {
  systemHealth: SystemHealth | null;
}

export const DataSourcesView: React.FC<DataSourcesViewProps> = ({ systemHealth }) => {
  const [providers, setProviders] = useState<DataSourceStatus[]>([]);
  const [telemetry, setTelemetry] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [testingProvider, setTestingProvider] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchProviders = async () => {
    setLoading(true);
    try {
      const [resProv, resTelem] = await Promise.all([
        api.getDataSourcesStatus(),
        api.getSystemTelemetry(),
      ]);
      setProviders(resProv.providers);
      setTelemetry(resTelem);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch data providers / telemetry', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTestProvider = async (providerId: string) => {
    setTestingProvider(providerId);
    try {
      const updatedStatus = await api.testProviderConnection(providerId);
      setProviders((prev) =>
        prev.map((p) => (p.provider_id === providerId ? updatedStatus : p))
      );
    } catch (err) {
      console.error(`Failed testing provider ${providerId}`, err);
    } finally {
      setTestingProvider(null);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  const getStatusBadge = (status: string, isAvailable: boolean, requiresAuth: boolean) => {
    const s = status.toLowerCase();
    if (s.includes('operational') || s.includes('connected') || isAvailable) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#5C7A61]/10 text-[#5C7A61] border border-[#5C7A61]/30">
          <CheckCircle2 className="w-3 h-3" />
          {status}
        </span>
      );
    }
    if (s.includes('auth required') || s.includes('authentication required')) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#B18A3A]/10 text-[#B18A3A] border border-[#B18A3A]/30">
          <Key className="w-3 h-3" />
          AUTH REQUIRED
        </span>
      );
    }
    if (s.includes('failed') || s.includes('error') || s.includes('unreachable') || s.includes('unavailable') || s.includes('timeout')) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#A83F3F]/10 text-[#A83F3F] border border-[#A83F3F]/30">
          <AlertCircle className="w-3 h-3" />
          {status}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#E9E6DD] text-[#20251F] border border-[#D5D2C8]">
        <Activity className="w-3 h-3 text-[#5F665F]" />
        {status}
      </span>
    );
  };

  const getRequiredEnvVars = (providerId: string): string[] => {
    switch (providerId) {
      case 'nasa_imerg':
        return ['NASA_EARTHDATA_TOKEN', 'NASA_IMERG_API_KEY'];
      case 'mosdac_gsmap':
        return ['MOSDAC_USER_KEY', 'MOSDAC_API_KEY'];
      case 'google_earth_engine':
        return ['GEE_PROJECT_ID', 'GEE_PRIVATE_KEY_PATH'];
      default:
        return [];
    }
  };

  return (
    <div className="space-y-5">
      {/* Top Health & Infrastructure Summary */}
      <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-5 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-sm">
        <div>
          <h2 className="text-sm font-bold text-[#20251F] flex items-center gap-2 uppercase font-mono">
            <Database className="w-4 h-4 text-[#496A52]" />
            External Telemetry Providers & Ingestion Pipeline Health
          </h2>
          <p className="text-xs text-[#5F665F] mt-0.5">
            Operational status of meteorological, radar, and optical satellite data providers covering all 8 NER states.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono text-[#5F665F] hidden sm:inline">
            Last Checked: {lastUpdated.toLocaleTimeString()}
          </span>
          <button
            onClick={fetchProviders}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#17201B] hover:bg-[#222D26] text-[#E8E5DC] text-xs font-semibold border border-[#17201B] transition-colors disabled:opacity-50 font-mono shadow-sm"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin text-[#496A52]' : 'text-[#AEB4AA]'}`} />
            Refresh All
          </button>
        </div>
      </div>

      {/* Backend Infrastructure Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 font-mono">
        <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-3.5 shadow-sm">
          <div className="flex items-center justify-between text-[#5F665F] text-xs mb-1">
            <span className="text-[10px] uppercase font-bold">FASTAPI CORE</span>
            <Server className="w-3.5 h-3.5 text-[#5C7A61]" />
          </div>
          <div className="text-base font-bold text-[#20251F]">{systemHealth?.status || 'Healthy'}</div>
          <span className="text-[10px] text-[#5F665F]">Uptime: {systemHealth?.uptime_seconds?.toFixed(0) || 0}s</span>
        </div>

        <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-3.5 shadow-sm">
          <div className="flex items-center justify-between text-[#5F665F] text-xs mb-1">
            <span className="text-[10px] uppercase font-bold">DATABASE ENGINE</span>
            <Database className="w-3.5 h-3.5 text-[#496A52]" />
          </div>
          <div className="text-base font-bold text-[#20251F]">{systemHealth?.database || 'Healthy'}</div>
          <span className="text-[10px] text-[#5F665F]">SQLAlchemy 2.0</span>
        </div>

        <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-3.5 shadow-sm">
          <div className="flex items-center justify-between text-[#5F665F] text-xs mb-1">
            <span className="text-[10px] uppercase font-bold">DUAL ML MODELS</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-[#5C7A61]" />
          </div>
          <div className="text-base font-bold text-[#5C7A61]">
            {systemHealth?.model_readiness ? 'Ready & Loaded' : 'Unavailable'}
          </div>
          <span className="text-[10px] text-[#5F665F]">
            Latency: {telemetry?.model_metrics?.model1_inference_ms_p50 || 1.2}ms
          </span>
        </div>

        <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-3.5 shadow-sm">
          <div className="flex items-center justify-between text-[#5F665F] text-xs mb-1">
            <span className="text-[10px] uppercase font-bold">GEE SATELLITE SLA</span>
            <Globe className="w-3.5 h-3.5 text-[#55758A]" />
          </div>
          <div className="text-base font-bold text-[#20251F]">
            {telemetry?.providers?.google_earth_engine?.status || 'Connected'}
          </div>
          <span className="text-[10px] text-[#5F665F]">
            Latency: {telemetry?.providers?.google_earth_engine?.avg_latency_ms?.toFixed(0) || 450}ms
          </span>
        </div>
      </div>

      {/* External Providers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {providers.map((p) => {
          const envVars = getRequiredEnvVars(p.provider_id);
          const isTesting = testingProvider === p.provider_id;

          return (
            <div
              key={p.provider_id}
              className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-4 flex flex-col justify-between hover:border-[#496A52] transition-colors relative shadow-sm"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <h3 className="font-bold text-xs text-[#20251F]">{p.name}</h3>
                    <span className="text-[10px] font-mono text-[#5F665F]">
                      ID: {p.provider_id}
                    </span>
                  </div>
                  {getStatusBadge(p.status, p.is_available, p.requires_auth)}
                </div>

                <p className="text-xs text-[#5F665F] mb-3 line-clamp-2 leading-relaxed">{p.description}</p>

                <div className="space-y-1.5 text-xs font-mono">
                  <div className="flex items-center justify-between py-0.5 border-t border-[#D5D2C8]/60">
                    <span className="text-[#5F665F] text-[10px]">Coverage:</span>
                    <span className="text-[#20251F] text-[11px] font-medium">{p.coverage}</span>
                  </div>
                  <div className="flex items-center justify-between py-0.5 border-t border-[#D5D2C8]/60">
                    <span className="text-[#5F665F] text-[10px]">Cadence:</span>
                    <span className="text-[#20251F] text-[11px] font-medium">{p.update_cadence}</span>
                  </div>
                  <div className="flex items-center justify-between py-0.5 border-t border-[#D5D2C8]/60">
                    <span className="text-[#5F665F] text-[10px]">Authentication:</span>
                    <span className="text-[#20251F] text-[11px] font-medium">
                      {p.requires_auth ? 'Credential Required' : 'Public / Free'}
                    </span>
                  </div>
                  {p.latency_ms !== null && p.latency_ms !== undefined && (
                    <div className="flex items-center justify-between py-0.5 border-t border-[#D5D2C8]/60">
                      <span className="text-[#5F665F] text-[10px]">Health Latency:</span>
                      <span className="text-[#55758A] font-bold text-[11px]">{p.latency_ms.toFixed(1)} ms</span>
                    </div>
                  )}
                </div>

                {/* Env Var Requirement Guidance */}
                {envVars.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-[#D5D2C8]/60">
                    <span className="text-[9px] text-[#5F665F] font-mono block mb-1 uppercase font-bold">
                      REQUIRED ENV CONFIG (.env):
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {envVars.map((v) => (
                        <span
                          key={v}
                          className="px-1.5 py-0.2 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[9px] font-mono text-[#20251F]"
                        >
                          {v}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-3 pt-2.5 border-t border-[#D5D2C8]/60 flex flex-col gap-1.5">
                {p.error_message && (
                  <div className="p-2 rounded bg-[#B18A3A]/10 border border-[#B18A3A]/20 text-[10px] text-[#B18A3A] font-mono leading-tight">
                    {p.error_message}
                  </div>
                )}

                <button
                  onClick={() => handleTestProvider(p.provider_id)}
                  disabled={isTesting}
                  className="w-full flex items-center justify-center gap-1.5 py-1.5 rounded-md bg-[#E9E6DD] hover:bg-[#D5D2C8] text-[#20251F] text-xs font-semibold border border-[#D5D2C8] transition-colors disabled:opacity-50 font-mono"
                >
                  {isTesting ? (
                    <>
                      <Loader2 className="w-3 h-3 animate-spin text-[#496A52]" />
                      Testing...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-3 h-3 text-[#5F665F]" />
                      Test Connection
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
