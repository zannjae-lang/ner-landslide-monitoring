import React, { useState, useEffect } from 'react';
import {
  Layers,
  Radio,
  Activity,
  CheckCircle2,
  Clock,
  Loader2,
  Info,
  AlertTriangle,
} from 'lucide-react';
import { api } from '../../services/api';

interface EvidenceFusionPanelProps {
  locationId: string;
  latitude: number;
  longitude: number;
  locationName?: string;
}

export const EvidenceFusionPanel: React.FC<EvidenceFusionPanelProps> = ({
  locationId,
  latitude,
  longitude,
  locationName,
}) => {
  const [evidenceData, setEvidenceData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvidence = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStationEvidence(locationId);
      setEvidenceData(data);
    } catch (err: any) {
      try {
        const evalData = await api.evaluateEvidence({
          location_id: locationId,
          latitude,
          longitude,
          location_name: locationName,
          include_satellite_check: true,
        });
        setEvidenceData(evalData);
      } catch (fallbackErr: any) {
        setError('Failed to compute multi-source evidence matrix.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (locationId) {
      fetchEvidence();
    }
  }, [locationId]);

  if (loading) {
    return (
      <div className="earth-panel p-5 flex items-center justify-center space-x-2 text-[#5F665F] py-8 font-mono text-xs">
        <Loader2 className="w-4 h-4 animate-spin text-[#496A52]" />
        <span>Aggregating multi-source satellite & ML evidence matrix...</span>
      </div>
    );
  }

  if (error || !evidenceData) {
    return (
      <div className="earth-panel p-3.5 flex items-center justify-between text-xs">
        <span className="text-[#5F665F]">Multi-source evidence summary ready for evaluation.</span>
        <button
          onClick={fetchEvidence}
          className="px-2.5 py-1 bg-[#FAF9F5] hover:bg-[#E9E6DD] text-[#496A52] rounded border border-[#D5D2C8] font-semibold text-xs font-mono"
        >
          Compute Evidence
        </button>
      </div>
    );
  }

  const getScoreColor = (score: number = 0) => {
    if (score >= 0.75) return 'text-[#A83F3F]';
    if (score >= 0.5) return 'text-[#C96B3D]';
    if (score >= 0.25) return 'text-[#B18A3A]';
    return 'text-[#5C7A61]';
  };

  const getConfidenceBadge = (confidence: string = 'MEDIUM') => {
    switch (confidence?.toUpperCase()) {
      case 'HIGH':
        return 'bg-[#EDF3EE] text-[#496A52] border-[#C8D8CB]';
      case 'MEDIUM':
        return 'bg-[#EBF1F5] text-[#55758A] border-[#C2D4E0]';
      case 'LOW':
        return 'bg-[#FAF5EB] text-[#B18A3A] border-[#E5D5B3]';
      default:
        return 'bg-[#E9E6DD] text-[#5F665F] border-[#D5D2C8]';
    }
  };

  const formatFactorName = (factorType: string = '', factorId: string = '') => {
    const raw = factorType || factorId;
    return raw
      .replace(/_/g, ' ')
      .toLowerCase()
      .replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const overallScore = evidenceData.overall_evidence_score ?? 0;
  const qualityScore = evidenceData.data_quality_score ?? 1.0;
  const evidenceLevel = evidenceData.evidence_level ?? 'Normal';
  const confidence = evidenceData.confidence ?? 'MEDIUM';
  const generatedAt = evidenceData.generated_at ? new Date(evidenceData.generated_at) : new Date();

  return (
    <div className="earth-panel p-4 space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 border-b border-[#D5D2C8] pb-2.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-[#E9E6DD] border border-[#D5D2C8] text-[#806B52]">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">
              Multi-Source Evidence Fusion Matrix
            </h3>
            <p className="text-[11px] text-[#5F665F]">
              Independent multi-modal verification (SAR + Optical + Hydrology + ML)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getConfidenceBadge(confidence)}`}>
            Confidence: {confidence} (Quality: {(qualityScore * 100).toFixed(0)}%)
          </span>
          <button
            onClick={fetchEvidence}
            className="p-1 rounded bg-[#FAF9F5] border border-[#D5D2C8] hover:bg-[#E9E6DD] text-[#5F665F] text-xs transition"
            title="Refresh Evidence"
          >
            <Activity className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Evidence Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 font-mono">
        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8] flex flex-col justify-between">
          <span className="text-[10px] font-semibold text-[#5F665F] uppercase tracking-wider">
            Overall Evidence Score
          </span>
          <div className="my-1">
            <span className={`text-2xl font-black ${getScoreColor(overallScore)}`}>
              {(overallScore * 100).toFixed(1)}%
            </span>
            <span className="text-xs text-[#889087] ml-1.5">/ 1.00</span>
          </div>
          <span className="text-[11px] font-semibold text-[#20251F] font-sans">
            Band: <strong className={getScoreColor(overallScore)}>{evidenceLevel}</strong>
          </span>
        </div>

        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8] flex flex-col justify-between">
          <span className="text-[10px] font-semibold text-[#5F665F] uppercase tracking-wider">
            Provenance & Confidence
          </span>
          <div className="my-1 text-xl font-black text-[#55758A]">
            {confidence}
          </div>
          <span className="text-[10px] text-[#889087] flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Evaluated: {generatedAt.toLocaleTimeString()}
          </span>
        </div>

        <div className="p-3 rounded bg-[#FAF9F5] border border-[#D5D2C8] flex flex-col justify-between">
          <span className="text-[10px] font-semibold text-[#5F665F] uppercase tracking-wider">
            Verification Protocol
          </span>
          <div className="my-1 text-xs font-semibold text-[#806B52] line-clamp-2 font-sans">
            {evidenceData.verification_requirement || 'Automated satellite and weather monitor active.'}
          </div>
          <span className="text-[10px] text-[#889087]">
            Status: {evidenceData.is_provisional ? 'Research Prototype' : 'Operational'}
          </span>
        </div>
      </div>

      {/* 6-Factor Independent Factor Matrix */}
      <div>
        <h4 className="text-[10px] font-bold text-[#20251F] uppercase tracking-wider mb-2 flex items-center gap-1.5 font-mono">
          <Radio className="w-3.5 h-3.5 text-[#55758A]" />
          Independent Evidence Factor Decomposition ({evidenceData.factors?.length || 6} Signals)
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          {evidenceData.factors &&
            evidenceData.factors.map((f: any) => {
              const score = f.indicator_score ?? f.anomaly_score ?? 0;
              return (
                <div
                  key={f.factor_id}
                  className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8] flex flex-col justify-between hover:border-[#806B52] transition"
                >
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-[#20251F]">
                        {formatFactorName(f.factor_type, f.factor_id)}
                      </span>
                      <span className="text-[10px] font-mono text-[#5F665F] bg-[#E9E6DD] px-1.5 py-0.2 rounded border border-[#D5D2C8]">
                        w: {f.weight}
                      </span>
                    </div>
                    <p className="text-[11px] text-[#5F665F] mb-1.5 leading-relaxed font-sans">{f.interpretation}</p>
                  </div>

                  <div className="pt-1.5 border-t border-[#E2DFD5] flex items-center justify-between text-[10px] font-mono">
                    <span className="text-[#889087]">Signal Score:</span>
                    <span className={`font-bold ${score >= 0.5 ? 'text-[#B18A3A]' : 'text-[#20251F]'}`}>
                      {(score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Supporting vs Conflicting Signals Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
        {/* Supporting Factors */}
        <div className="p-3 rounded bg-[#EDF3EE] border border-[#C8D8CB]">
          <span className="font-bold text-[#496A52] mb-1 flex items-center gap-1.5 text-xs font-mono">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#496A52]" />
            SUPPORTING RISK SIGNALS ({evidenceData.supporting_factors?.length || 0})
          </span>
          <ul className="space-y-1 mt-1.5">
            {evidenceData.supporting_factors?.length > 0 ? (
              evidenceData.supporting_factors.map((item: string, idx: number) => (
                <li key={idx} className="text-[#20251F] flex items-start gap-1.5 text-[11px]">
                  <span className="text-[#496A52] font-bold">&bull;</span>
                  {item}
                </li>
              ))
            ) : (
              <li className="text-[#889087] text-[11px]">No critical triggering factors identified.</li>
            )}
          </ul>
        </div>

        {/* Conflicting / Missing Signals */}
        <div className="p-3 rounded bg-[#FAF5EB] border border-[#E5D5B3]">
          <span className="font-bold text-[#B18A3A] mb-1 flex items-center gap-1.5 text-xs font-mono">
            <AlertTriangle className="w-3.5 h-3.5 text-[#B18A3A]" />
            CONFLICTING / MISSING SIGNALS ({evidenceData.conflicting_factors?.length || 0})
          </span>
          <ul className="space-y-1 mt-1.5">
            {evidenceData.conflicting_factors?.length > 0 ? (
              evidenceData.conflicting_factors.map((item: string, idx: number) => (
                <li key={idx} className="text-[#20251F] flex items-start gap-1.5 text-[11px]">
                  <span className="text-[#B18A3A] font-bold">&bull;</span>
                  {item}
                </li>
              ))
            ) : (
              <li className="text-[#889087] text-[11px]">All active evidence data streams aligned.</li>
            )}
          </ul>
        </div>
      </div>

      {/* Decision Support Notice */}
      <div className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8] text-[10px] font-mono text-[#5F665F] flex items-start gap-2">
        <Info className="w-3.5 h-3.5 text-[#889087] mt-0.5 flex-shrink-0" />
        <span>
          <strong>Decision Support Notice:</strong> {evidenceData.scientific_disclaimer ||
            'Multi-source evidence fusion combines uncalibrated SAR backscatter variance, optical NDVI delta, and machine learning susceptibility. Satellite anomalies alone do not confirm slope failure and require ground-truth field verification.'}
        </span>
      </div>
    </div>
  );
};
