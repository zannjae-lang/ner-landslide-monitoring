import React from 'react';
import {
  Cpu,
  Sliders,
  AlertTriangle,
  Info,
} from 'lucide-react';

export const ModelRegistryView: React.FC = () => {
  return (
    <div className="space-y-5">
      {/* Top Banner */}
      <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-5 shadow-sm">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-sm font-bold text-[#20251F] flex items-center gap-2 uppercase font-mono">
              <Cpu className="w-4 h-4 text-[#496A52]" />
              Machine Learning Model Registry & Scientific Validation
            </h2>
            <p className="text-xs text-[#5F665F] mt-0.5">
              Deterministic Joblib pipeline artifacts and feature schemas governing landslide susceptibility and dynamic early warning.
            </p>
          </div>
          <span className="text-[10px] font-mono bg-[#B18A3A]/10 text-[#B18A3A] border border-[#B18A3A]/30 px-2 py-0.5 rounded font-semibold uppercase">
            Prototype Research Candidates
          </span>
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Model 1: Susceptibility */}
        <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-5 space-y-3.5 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#D5D2C8] pb-3">
            <div>
              <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">Model 1: Landslide Susceptibility Model</h3>
              <span className="text-[10px] font-mono text-[#5F665F]">version: model1_v1.0 &bull; XGBoost Pipeline</span>
            </div>
            <span className="text-[10px] font-mono bg-[#E9E6DD] text-[#496A52] border border-[#D5D2C8] px-2 py-0.5 rounded uppercase font-semibold">
              Static Spatial
            </span>
          </div>

          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Objective / Task:</span>
              <span className="text-[#20251F] font-medium">Static susceptibility prediction (terrain & environmental features)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Artifact File:</span>
              <span className="font-mono text-[#20251F] text-[11px]">model1_landslide_susceptibility.joblib</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Decision Threshold:</span>
              <span className="font-mono text-[#B18A3A] font-bold">0.39 (39%)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Operational Certification:</span>
              <span className="font-mono text-[#A83F3F]">False (Research Prototype)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Probability Calibration:</span>
              <span className="font-mono text-[#B18A3A]">Uncalibrated Output</span>
            </div>
          </div>

          <div>
            <h4 className="text-[10px] font-mono font-bold text-[#20251F] uppercase mb-1.5">
              13 Enforced Features (Strict Order):
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1 text-[10px] font-mono">
              {[
                '1. elevation',
                '2. slope',
                '3. curvature',
                '4. tpi',
                '5. tri',
                '6. aspect_sin',
                '7. aspect_cos',
                '8. ndvi_p90',
                '9. ndvi_p50',
                '10. ndvi_p10',
                '11. distance_to_road_m',
                '12. distance_to_drainage_m',
                '13. lulc_type',
              ].map((item) => (
                <div key={item} className="bg-[#E9E6DD] p-1.5 rounded border border-[#D5D2C8] text-[#20251F]">
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-md bg-[#E9E6DD]/60 border border-[#D5D2C8] text-[10px] font-mono text-[#5F665F] space-y-0.5">
            <div className="font-semibold text-[#20251F] flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-[#55758A]" />
              Scientific Notes:
            </div>
            <p className="leading-relaxed font-sans">
              Trained on spatial terrain rasters and land-cover classes. Topographic proxies (curvature, TPI, TRI) require identical neighborhood definitions for exact parity.
            </p>
          </div>
        </div>

        {/* Model 2: Dynamic Early Warning */}
        <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-5 space-y-3.5 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#D5D2C8] pb-3">
            <div>
              <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">Model 2: Dynamic Early Warning Model</h3>
              <span className="text-[10px] font-mono text-[#5F665F]">version: model2_v1.0_temporal_candidate &bull; XGBoost</span>
            </div>
            <span className="text-[10px] font-mono bg-[#E9E6DD] text-[#55758A] border border-[#D5D2C8] px-2 py-0.5 rounded uppercase font-semibold">
              Dynamic Temporal
            </span>
          </div>

          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Objective / Task:</span>
              <span className="text-[#20251F] font-medium">Dynamic warning probability candidate from weather triggers</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Artifact File:</span>
              <span className="font-mono text-[#20251F] text-[11px]">model2_landslide_early_warning.joblib</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Prototype Threshold:</span>
              <span className="font-mono text-[#55758A] font-bold">0.10 (10%)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">Operational Certification:</span>
              <span className="font-mono text-[#A83F3F]">False (Research Prototype)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-[#D5D2C8]/60">
              <span className="text-[#5F665F]">SAR Integration:</span>
              <span className="font-mono text-[#5F665F]">Excluded (Preserves Parity)</span>
            </div>
          </div>

          <div>
            <h4 className="text-[10px] font-mono font-bold text-[#20251F] uppercase mb-1.5">
              10 Enforced Features (Strict Order):
            </h4>
            <div className="grid grid-cols-2 gap-1 text-[10px] font-mono">
              {[
                '1. Rainfall_1h (mm)',
                '2. Rainfall_3h (mm)',
                '3. Rainfall_6h (mm)',
                '4. Rainfall_12h (mm)',
                '5. Rainfall_24h (mm)',
                '6. Rainfall_3day (mm)',
                '7. Rainfall_7day (mm)',
                '8. susceptibility_probability (Model 1)',
                '9. soil_moisture_layer_1 (0-7cm)',
                '10. soil_moisture_layer_2 (7-28cm)',
              ].map((item) => (
                <div key={item} className="bg-[#E9E6DD] p-1.5 rounded border border-[#D5D2C8] text-[#20251F]">
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-md bg-[#E9E6DD]/60 border border-[#D5D2C8] text-[10px] font-mono text-[#5F665F] space-y-0.5">
            <div className="font-semibold text-[#20251F] flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-[#B18A3A]" />
              Known Research Limitations:
            </div>
            <p className="leading-relaxed font-sans">
              Trained with GSI event inventory records. Negative samples are pseudo-negative/synthetic. Performance varies across rolling temporal validation windows; uncalibrated for public emergency alerts.
            </p>
          </div>
        </div>
      </div>

      {/* Risk Engine 2.0 Fusion Math Documentation */}
      <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded-lg p-5 shadow-sm">
        <h3 className="font-bold text-xs text-[#20251F] uppercase tracking-wider mb-1 flex items-center gap-1.5 font-mono">
          <Sliders className="w-4 h-4 text-[#496A52]" />
          Risk Engine 2.0 Multi-Factor Fusion Architecture
        </h3>
        <p className="text-xs text-[#5F665F] mb-3">
          Combines static susceptibility probability, dynamic warning probability candidate, and 24-hour rainfall triggers with strict data freshness verification.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs">
          <div className="p-3.5 rounded-md bg-[#E9E6DD]/60 border border-[#D5D2C8]">
            <span className="text-[#5F665F] block mb-1 text-[10px]">FUSION FORMULA:</span>
            <div className="text-[#20251F] font-bold text-xs">
              Score = 0.45 &times; P_susc + 0.55 &times; P_dyn + &Delta;_rain
            </div>
            <span className="text-[10px] text-[#5F665F] mt-2 block">Clipped strictly to [0.0, 1.0]</span>
          </div>

          <div className="p-3.5 rounded-md bg-[#E9E6DD]/60 border border-[#D5D2C8]">
            <span className="text-[#5F665F] block mb-1 text-[10px]">RAINFALL ADJUSTMENT (&Delta;):</span>
            <div className="space-y-0.5 text-[#20251F] text-[10px]">
              <div>&ge;65 mm: +0.15 (Critical)</div>
              <div>&ge;35 mm: +0.10 (High)</div>
              <div>&ge;15 mm: +0.05 (Elevated)</div>
              <div>&lt;15 mm: +0.00 (Low)</div>
            </div>
          </div>

          <div className="p-3.5 rounded-md bg-[#E9E6DD]/60 border border-[#D5D2C8]">
            <span className="text-[#5F665F] block mb-1 text-[10px]">DATA FRESHNESS CEILING:</span>
            <div className="text-[#B18A3A] font-bold text-xs">Max 6.0 Hours</div>
            <span className="text-[10px] text-[#5F665F] mt-1 block">
              Data &gt;6h is flagged STALE; missing inputs flagged UNAVAILABLE.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
