import React, { useState } from 'react';
import {
  Bell,
  ShieldCheck,
  ArrowUpRight,
} from 'lucide-react';
import { AlertRecord } from '../../types';
import { api } from '../../services/api';
import { RiskBadge } from '../common/RiskBadge';

interface AlertsCenterProps {
  alerts: AlertRecord[];
  onRefreshAlerts: () => void;
  onInspectStation: (locationId: string) => void;
}

export const AlertsCenter: React.FC<AlertsCenterProps> = ({
  alerts,
  onRefreshAlerts,
  onInspectStation,
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const filteredAlerts = alerts.filter((a) => {
    const matchesSeverity = severityFilter === 'all' || a.severity === severityFilter;
    const matchesStatus = statusFilter === 'all' || a.status === statusFilter;
    return matchesSeverity && matchesStatus;
  });

  const handleUpdateStatus = async (alertId: string, newStatus: 'acknowledged' | 'resolved') => {
    setActionLoading(alertId);
    try {
      await api.updateAlertStatus(alertId, newStatus, `Updated via Command Console`);
      onRefreshAlerts();
    } catch (err) {
      console.error('Failed to update alert status', err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-5">
      {/* Header & Filter Controls */}
      <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-sm">
        <div>
          <h2 className="text-sm font-bold text-[#20251F] flex items-center gap-2 uppercase font-mono">
            <Bell className="w-4 h-4 text-[#B18A3A]" />
            Early Warning Alert Queue & Incident Audit Ledger
          </h2>
          <p className="text-xs text-[#5F665F] mt-0.5">
            Automated alerts dispatched when fused prototype threat reaches Watch (≥0.25), Alert (≥0.50), or Critical (≥0.75).
          </p>
        </div>

        {/* Filter Toolbar */}
        <div className="flex flex-wrap items-center gap-2.5 font-mono text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-[#5F665F] text-[10px] uppercase font-bold">SEVERITY:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-[#E9E6DD] border border-[#D5D2C8] text-[#20251F] text-xs rounded-md px-2.5 py-1 focus:outline-none focus:border-[#496A52]"
            >
              <option value="all">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="Alert">Alert</option>
              <option value="Watch">Watch</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-[#5F665F] text-[10px] uppercase font-bold">STATUS:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-[#E9E6DD] border border-[#D5D2C8] text-[#20251F] text-xs rounded-md px-2.5 py-1 focus:outline-none focus:border-[#496A52]"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alerts Ledger Table */}
      <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[10px] text-[#5F665F] border-b border-[#D5D2C8] bg-[#E9E6DD] font-mono uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-2.5 px-3.5">Severity</th>
                <th className="py-2.5 px-3.5">Station / Region</th>
                <th className="py-2.5 px-3.5">Trigger Summary</th>
                <th className="py-2.5 px-3.5">Threat Score</th>
                <th className="py-2.5 px-3.5">Lifecycle</th>
                <th className="py-2.5 px-3.5">Timestamp (IST)</th>
                <th className="py-2.5 px-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#D5D2C8]">
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-10 text-center text-[#5F665F] text-xs font-mono">
                    <ShieldCheck className="w-7 h-7 mx-auto mb-2 text-[#5C7A61]/50" />
                    No alert records match the selected filter criteria.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-[#E9E6DD]/60 transition-colors">
                    <td className="py-3 px-3.5">
                      <RiskBadge level={alert.severity} size="sm" />
                    </td>
                    <td className="py-3 px-3.5">
                      <div className="font-bold text-[#20251F] text-xs font-sans">{alert.location_name}</div>
                      <div className="text-[10px] text-[#5F665F] font-mono">
                        {alert.district}, {alert.state}
                      </div>
                    </td>
                    <td className="py-3 px-3.5 max-w-sm">
                      <p className="text-[#20251F] leading-snug line-clamp-2 font-sans">{alert.message}</p>
                    </td>
                    <td className="py-3 px-3.5 font-mono font-bold text-[#806B52] text-xs">
                      {(alert.score * 100).toFixed(0)}%
                    </td>
                    <td className="py-3 px-3.5">
                      <span
                        className={`inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold uppercase font-mono ${
                          alert.status === 'active'
                            ? 'bg-[#A83F3F]/10 text-[#A83F3F] border border-[#A83F3F]/30'
                            : alert.status === 'acknowledged'
                            ? 'bg-[#B18A3A]/10 text-[#B18A3A] border border-[#B18A3A]/30'
                            : 'bg-[#5C7A61]/10 text-[#5C7A61] border border-[#5C7A61]/30'
                        }`}
                      >
                        {alert.status}
                      </span>
                    </td>
                    <td className="py-3 px-3.5 text-[#5F665F] font-mono text-[10px]">
                      {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })},{' '}
                      {new Date(alert.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                    </td>
                    <td className="py-3 px-3.5 text-right font-mono">
                      <div className="flex items-center justify-end gap-1">
                        {alert.status === 'active' && (
                          <button
                            onClick={() => handleUpdateStatus(alert.id, 'acknowledged')}
                            disabled={actionLoading === alert.id}
                            className="px-2 py-0.5 rounded bg-[#B18A3A]/10 hover:bg-[#B18A3A]/20 text-[#B18A3A] border border-[#B18A3A]/30 text-[10px] font-semibold transition-colors"
                          >
                            Ack
                          </button>
                        )}
                        {alert.status !== 'resolved' && (
                          <button
                            onClick={() => handleUpdateStatus(alert.id, 'resolved')}
                            disabled={actionLoading === alert.id}
                            className="px-2 py-0.5 rounded bg-[#5C7A61]/10 hover:bg-[#5C7A61]/20 text-[#5C7A61] border border-[#5C7A61]/30 text-[10px] font-semibold transition-colors"
                          >
                            Resolve
                          </button>
                        )}
                        <button
                          onClick={() => onInspectStation(alert.location_id)}
                          className="p-1 rounded bg-[#E9E6DD] hover:bg-[#D5D2C8] text-[#20251F] border border-[#D5D2C8] transition-colors"
                          title="Inspect telemetry"
                        >
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
