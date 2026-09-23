import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  CheckSquare,
  HelpCircle,
  ArrowUpRight,
  Loader2,
  X,
} from 'lucide-react';
import { api } from '../../services/api';

interface ExplainabilityDrawerProps {
  locationId: string;
  isOpen: boolean;
  onClose: () => void;
  locationName?: string;
}

export const ExplainabilityDrawer: React.FC<ExplainabilityDrawerProps> = ({
  locationId,
  isOpen,
  onClose,
  locationName,
}) => {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen && locationId) {
      setLoading(true);
      api
        .getStationExplainableReport(locationId)
        .then((res) => setReport(res))
        .catch(() => {
          api
            .generateExplainableReport({
              latitude: 26.2,
              longitude: 92.9,
              location_id: locationId,
              location_name: locationName,
            })
            .then((res) => setReport(res))
            .catch((err) => console.error('Failed to load explainability report', err));
        })
        .finally(() => setLoading(false));
    }
  }, [isOpen, locationId]);

  if (!isOpen) return null;

  const m1Features = report?.model1_susceptibility_explainability?.top_contributing_features || [];
  const m2Features = report?.model2_dynamic_explainability?.top_contributing_features || [];
  const allAttributions = [...m1Features, ...m2Features];

  const sopActions: string[] = report?.recommended_sop_actions || [
    'Activate District Disaster Management Authority (DDMA) emergency monitoring.',
    'Issue travel advisory for vulnerable highway segments.',
    'Dispatch field response team to inspect active tension cracks.',
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/40 backdrop-blur-xs animate-fade-in">
      <div className="w-full max-w-xl h-full bg-[#FAF9F5] border-l border-[#D5D2C8] p-5 flex flex-col justify-between overflow-y-auto shadow-xl">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-[#D5D2C8] pb-3">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[#55758A]">
                <BrainCircuit className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">
                  Explainable AI & DDMA Audit Brief
                </h3>
                <p className="text-[11px] text-[#5F665F]">
                  Feature attribution and causal analysis for {locationName || locationId}
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

          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center space-y-2 text-[#5F665F] font-mono text-xs">
              <Loader2 className="w-5 h-5 animate-spin text-[#496A52]" />
              <span>Decomposing AI feature attributions & DDMA response actions...</span>
            </div>
          ) : report ? (
            <div className="space-y-3.5">
              {/* Executive Summary Card */}
              <div className="p-3 rounded bg-[#EBF1F5] border border-[#C2D4E0]">
                <span className="text-[10px] font-semibold text-[#55758A] uppercase tracking-wider block mb-0.5 font-mono">
                  Executive Risk Interpretation
                </span>
                <p className="text-xs text-[#20251F] leading-relaxed font-medium">
                  {report.executive_summary_narrative ||
                    'Elevated landslide probability triggered by high antecedent precipitation on steep terrain. Immediate monitoring recommended.'}
                </p>
              </div>

              {/* Key Risk Drivers Pill List */}
              {report.key_risk_drivers?.length > 0 && (
                <div>
                  <h4 className="text-[10px] font-bold text-[#20251F] uppercase tracking-wider mb-1.5 font-mono">
                    Identified Causal Drivers
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {report.key_risk_drivers.map((driver: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded bg-[#FAF5EB] border border-[#E5D5B3] text-[#806B52] text-[11px] font-medium font-mono"
                      >
                        {driver}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Top Driving Factors Breakdown */}
              <div>
                <h4 className="text-[10px] font-bold text-[#20251F] uppercase tracking-wider mb-2 flex items-center gap-1.5 font-mono">
                  <ArrowUpRight className="w-3.5 h-3.5 text-[#B18A3A]" />
                  Primary Contributing Drivers ({allAttributions.length})
                </h4>
                <div className="space-y-1.5">
                  {allAttributions.length > 0 ? (
                    allAttributions.map((f: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-2 rounded bg-[#FAF9F5] border border-[#D5D2C8] flex items-center justify-between"
                      >
                        <div>
                          <span className="font-semibold text-xs text-[#20251F] block">
                            {f.feature_display_name || f.feature_name}
                          </span>
                          <span className="text-[10px] text-[#5F665F]">{f.plain_language_impact}</span>
                        </div>
                        <span className="text-[10px] font-mono font-bold text-[#806B52] bg-[#FAF5EB] px-2 py-0.5 rounded border border-[#E5D5B3]">
                          {((f.relative_importance_score || 0.25) * 100).toFixed(0)}% Impact
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-[#5F665F] p-2.5 bg-[#E9E6DD] rounded font-mono">
                      Standard topographic baseline with active precipitation monitoring.
                    </div>
                  )}
                </div>
              </div>

              {/* DDMA Recommended Response Actions Checklist */}
              <div>
                <h4 className="text-[10px] font-bold text-[#20251F] uppercase tracking-wider mb-2 flex items-center gap-1.5 font-mono">
                  <CheckSquare className="w-3.5 h-3.5 text-[#496A52]" />
                  DDMA Standard Operating Procedures (SOP)
                </h4>
                <div className="space-y-1.5">
                  {sopActions.map((act: string, idx: number) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded bg-[#EDF3EE] border border-[#C8D8CB] flex items-start gap-2 text-xs text-[#20251F]"
                    >
                      <span className="w-4 h-4 rounded-full bg-[#496A52] text-[#FAF9F5] font-bold flex items-center justify-center flex-shrink-0 text-[10px] font-mono">
                        {idx + 1}
                      </span>
                      <strong className="block text-[#20251F] font-normal">{act}</strong>
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Transparency & Limitations */}
              <div className="p-2.5 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[10px] font-mono text-[#5F665F] space-y-0.5">
                <div className="flex items-center gap-1.5 font-bold text-[#20251F]">
                  <HelpCircle className="w-3.5 h-3.5 text-[#55758A]" />
                  Algorithmic Attribution Notice
                </div>
                <p className="leading-relaxed font-sans">
                  {report.disclaimer ||
                    'Feature impact scores are derived from heuristic sensitivity analysis and local tree splits in Model 1 (XGBoost v1.0) and Model 2 (Temporal Early-Warning). Model outputs represent early-warning indicators and must be validated alongside official IMD/GSI bulletins.'}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-[#889087] text-xs py-10 text-center font-mono">Unable to load explainability report.</div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="pt-3 border-t border-[#D5D2C8] flex items-center justify-between gap-2.5">
          <span className="text-[10px] font-mono text-[#889087]">Report ID: {report?.report_id || 'EXP-AUDIT-2026'}</span>
          <button
            onClick={onClose}
            className="px-3.5 py-1 bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] rounded font-semibold text-xs transition font-mono"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
