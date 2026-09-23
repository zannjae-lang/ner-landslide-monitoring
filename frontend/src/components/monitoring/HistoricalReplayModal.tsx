import React, { useState, useEffect } from 'react';
import {
  History,
  Play,
  CloudRain,
  X,
  Loader2,
  Info,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { api } from '../../services/api';

interface HistoricalReplayModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HistoricalReplayModal: React.FC<HistoricalReplayModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string>('mizoram_remal_2024');
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [runningSim, setRunningSim] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      api
        .getHistoricalEvents()
        .then((res) => {
          const list = res.events || [];
          setEvents(list);
          if (list.length > 0 && !selectedEventId) {
            setSelectedEventId(list[0].event_id);
          }
        })
        .catch((err) => console.error('Failed to load historical disaster catalog', err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  const handleRunSimulation = async (eventId: string) => {
    setRunningSim(true);
    try {
      const res = await api.simulateHistoricalEvent(eventId);
      setSimulationResult(res);
    } catch (err) {
      console.error('Failed to run disaster replay simulation', err);
    } finally {
      setRunningSim(false);
    }
  };

  useEffect(() => {
    if (selectedEventId && isOpen) {
      handleRunSimulation(selectedEventId);
    }
  }, [selectedEventId, isOpen]);

  if (!isOpen) return null;

  const currentEvent = events.find((e) => e.event_id === selectedEventId) || simulationResult?.event_details;

  const chartData = simulationResult?.timeline?.map((t: any) => ({
    day: `Day ${t.day_offset >= 0 ? '+' : ''}${t.day_offset}`,
    date: t.date_str || `Day ${t.day_offset}`,
    rainfall_24h: t.rainfall_24h_mm ?? 0,
    risk_score: +((t.simulated_risk_score ?? 0) * 100).toFixed(1),
    dynamic_prob: +((t.simulated_dynamic_prob ?? 0) * 100).toFixed(1),
    risk_level: t.simulated_risk_level || 'Normal',
  })) || [];

  const peakRiskScore = simulationResult?.peak_combined_risk_score ?? 0.85;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-fade-in">
      <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded max-w-3xl w-full max-h-[90vh] flex flex-col justify-between overflow-hidden shadow-xl">
        {/* Header */}
        <div className="p-3.5 border-b border-[#D5D2C8] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded bg-[#FAF5EB] border border-[#E5D5B3] text-[#B18A3A]">
              <History className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">
                Historical Disaster Replay & Benchmark Engine
              </h3>
              <p className="text-[11px] text-[#5F665F]">
                Retrospective timeline simulation against verified Northeast landslide catastrophes
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded bg-[#E9E6DD] border border-[#D5D2C8] hover:bg-[#D5D2C8] text-[#20251F] transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-3.5 overflow-y-auto space-y-3.5 flex-1">
          {/* Disaster Event Selector Tabs */}
          <div>
            <label className="text-[10px] font-mono font-semibold text-[#5F665F] uppercase tracking-wider block mb-1.5">
              VERIFIED HISTORICAL SCENARIOS:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-1.5">
              {events.map((ev) => (
                <button
                  key={ev.event_id}
                  onClick={() => setSelectedEventId(ev.event_id)}
                  className={`p-2 rounded text-left border transition-all ${
                    selectedEventId === ev.event_id
                      ? 'bg-[#17201B] border-[#17201B] text-[#FAF9F5]'
                      : 'bg-[#E9E6DD] border-[#D5D2C8] text-[#20251F] hover:border-[#806B52]'
                  }`}
                >
                  <span className="font-bold text-xs block truncate">{ev.event_name}</span>
                  <span className="text-[10px] block mt-0.5 font-mono opacity-80">
                    {ev.state} &bull; {ev.event_date}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Current Event Context Banner */}
          {currentEvent && (
            <div className="p-3 rounded bg-[#E9E6DD] border border-[#D5D2C8] flex flex-col md:flex-row md:items-center justify-between gap-2.5">
              <div>
                <div className="flex items-center gap-1.5 mb-0.5">
                  <span className="text-xs font-bold text-[#20251F]">{currentEvent.event_name}</span>
                  <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-[#FBF0F0] text-[#A83F3F] border border-[#E8B8B8]">
                    VERIFIED DISASTER
                  </span>
                </div>
                <p className="text-xs text-[#5F665F] leading-relaxed max-w-xl font-sans">
                  {currentEvent.reported_impact || currentEvent.geological_setting || 'Extreme monsoon landslide event in the North Eastern Region.'}
                </p>
                <div className="flex flex-wrap gap-2 mt-1.5 text-[10px] font-mono text-[#5F665F]">
                  <span>Location: {currentEvent.location_name} ({currentEvent.district}, {currentEvent.state})</span>
                  <span>&bull; Peak 24h Rain: {currentEvent.triggering_rainfall_24h_mm || 180} mm</span>
                </div>
              </div>

              <button
                onClick={() => handleRunSimulation(selectedEventId)}
                disabled={runningSim}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] font-bold text-xs transition disabled:opacity-50 flex-shrink-0 font-mono"
              >
                {runningSim ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Play className="w-3.5 h-3.5 fill-[#FAF9F5]" />
                )}
                {runningSim ? 'Simulating...' : 'Replay Event'}
              </button>
            </div>
          )}

          {/* Simulation Timeline Chart */}
          {simulationResult && (
            <div className="space-y-2.5">
              <div className="flex items-center justify-between font-mono">
                <h4 className="text-[10px] font-bold text-[#20251F] uppercase tracking-wider flex items-center gap-1.5">
                  <CloudRain className="w-3.5 h-3.5 text-[#55758A]" />
                  7-Day Risk & Precipitation Trajectory
                </h4>
                <span className="text-[10px] text-[#806B52] font-bold">
                  Peak Threat: {(peakRiskScore * 100).toFixed(1)}% ({simulationResult.peak_risk_level || 'Critical'})
                </span>
              </div>

              <div className="h-52 w-full bg-[#FAF9F5] p-2.5 rounded border border-[#D5D2C8]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E2DFD5" />
                    <XAxis dataKey="day" stroke="#5F665F" fontSize={10} fontStyle="monospace" />
                    <YAxis stroke="#5F665F" fontSize={10} fontStyle="monospace" />
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
                    <Line
                      type="monotone"
                      dataKey="risk_score"
                      name="Fused Threat (%)"
                      stroke="#B18A3A"
                      strokeWidth={2.5}
                      dot={{ r: 2.5, fill: '#B18A3A' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="rainfall_24h"
                      name="24h Rain (mm)"
                      stroke="#55758A"
                      strokeWidth={1.5}
                      dot={{ r: 2, fill: '#55758A' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Day-by-Day Timeline Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-1 font-mono">
                {simulationResult.timeline?.map((step: any, idx: number) => {
                  const score = step.simulated_risk_score ?? 0;
                  const isCritical = score >= 0.75;
                  return (
                    <div
                      key={idx}
                      className={`p-1.5 rounded border text-center text-xs ${
                        isCritical
                          ? 'bg-[#FBF0F0] border-[#E8B8B8] text-[#A83F3F]'
                          : 'bg-[#FAF9F5] border-[#D5D2C8] text-[#20251F]'
                      }`}
                    >
                      <span className="text-[9px] font-bold block mb-0.5 text-[#5F665F]">
                        Day {step.day_offset >= 0 ? `+${step.day_offset}` : step.day_offset}
                      </span>
                      <span className="text-xs font-black block">
                        {(score * 100).toFixed(0)}%
                      </span>
                      <span className="text-[9px] text-[#55758A] block">
                        {step.rainfall_24h_mm?.toFixed(0) || 0}mm
                      </span>
                      <span className="text-[8px] font-bold uppercase block mt-0.5">
                        {step.simulated_risk_level || 'Normal'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Validation Disclaimer */}
          <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8] text-[10px] font-mono text-[#5F665F] flex items-start gap-2">
            <Info className="w-3.5 h-3.5 text-[#889087] mt-0.5 flex-shrink-0" />
            <span>
              <strong>Replay Methodology Notice:</strong> {simulationResult?.scientific_caveat ||
                'Disaster replays utilize verified historical rainfall sequences coupled with static Copernicus DEM topography to demonstrate how Model 1, Model 2, and the Risk Engine respond to real-world extreme precipitation events.'}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-[#D5D2C8] bg-[#E9E6DD] flex items-center justify-between text-xs font-mono">
          <span className="text-[10px] text-[#5F665F]">
            SIH 2026 Problem Statement 26001 Benchmark Suite
          </span>
          <button
            onClick={onClose}
            className="px-3 py-1 bg-[#FAF9F5] hover:bg-[#FAF9F5]/80 text-[#20251F] font-semibold rounded text-xs transition border border-[#D5D2C8]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
