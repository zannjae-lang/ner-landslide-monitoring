import React, { useState, useEffect } from 'react';
import {
  Camera,
  AlertOctagon,
  CheckCircle2,
  Clock,
  X,
  Loader2,
  Send,
} from 'lucide-react';
import { api } from '../../services/api';

interface FieldEvidenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultLocation?: {
    locationId?: string;
    latitude?: number;
    longitude?: number;
    locationName?: string;
    state?: string;
    district?: string;
  };
}

export const FieldEvidenceModal: React.FC<FieldEvidenceModalProps> = ({
  isOpen,
  onClose,
  defaultLocation,
}) => {
  const [activeTab, setActiveTab] = useState<'submit' | 'list'>('submit');
  const [latitude, setLatitude] = useState<number>(defaultLocation?.latitude || 26.2006);
  const [longitude, setLongitude] = useState<number>(defaultLocation?.longitude || 92.9376);
  const [locationName, setLocationName] = useState<string>(defaultLocation?.locationName || '');
  const [stateName, setStateName] = useState<string>(defaultLocation?.state || 'Assam');
  const [district, setDistrict] = useState<string>(defaultLocation?.district || 'Dima Hasao');
  const [category, setCategory] = useState<string>('VISIBLE_CRACK');
  const [severity, setSeverity] = useState<string>('Moderate');
  const [description, setDescription] = useState<string>('');
  const [reporterName, setReporterName] = useState<string>('');
  const [reporterRole, setReporterRole] = useState<string>('field_officer');
  const [imageUrl, setImageUrl] = useState<string>('');

  const [submitting, setSubmitting] = useState<boolean>(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [recentReports, setRecentReports] = useState<any[]>([]);
  const [loadingReports, setLoadingReports] = useState<boolean>(false);

  useEffect(() => {
    if (defaultLocation) {
      if (defaultLocation.latitude) setLatitude(defaultLocation.latitude);
      if (defaultLocation.longitude) setLongitude(defaultLocation.longitude);
      if (defaultLocation.locationName) setLocationName(defaultLocation.locationName);
      if (defaultLocation.state) setStateName(defaultLocation.state);
      if (defaultLocation.district) setDistrict(defaultLocation.district);
    }
  }, [defaultLocation]);

  const loadRecentReports = async () => {
    setLoadingReports(true);
    try {
      const res = await api.getFieldReports({ limit: 10 } as any);
      setRecentReports(res.items || []);
    } catch (err) {
      console.error('Failed to load field reports', err);
    } finally {
      setLoadingReports(false);
    }
  };

  useEffect(() => {
    if (isOpen && activeTab === 'list') {
      loadRecentReports();
    }
  }, [isOpen, activeTab]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) {
      setErrorMsg('Please provide an observation description.');
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      await api.submitFieldReport({
        location_id: defaultLocation?.locationId,
        latitude,
        longitude,
        location_name: locationName || 'Field Observation Site',
        state: stateName,
        district,
        observation_category: category,
        severity,
        description,
        reporter_name: reporterName || 'Field Officer',
        reporter_role: reporterRole,
        photo_url: imageUrl || undefined,
      });

      setSuccessMsg('Field ground-truth report submitted successfully for DDMA verification.');
      setDescription('');
      setTimeout(() => {
        setActiveTab('list');
        loadRecentReports();
      }, 1200);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail || 'Failed to submit field report.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-fade-in">
      <div className="bg-[#FAF9F5] border border-[#D5D2C8] rounded max-w-xl w-full max-h-[88vh] flex flex-col justify-between overflow-hidden shadow-xl">
        {/* Header */}
        <div className="p-3.5 border-b border-[#D5D2C8] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded bg-[#EDF3EE] border border-[#C8D8CB] text-[#496A52]">
              <Camera className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-xs text-[#20251F] uppercase font-mono">
                Field Ground-Truth & Evidence Intake
              </h3>
              <p className="text-[11px] text-[#5F665F]">
                Submit and audit localized ground observations, tension cracks & slumps
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

        {/* Tab Switcher */}
        <div className="px-3.5 pt-1.5 border-b border-[#D5D2C8] flex items-center gap-3 bg-[#E9E6DD] text-xs font-mono">
          <button
            onClick={() => setActiveTab('submit')}
            className={`pb-1.5 border-b-2 transition font-semibold ${
              activeTab === 'submit'
                ? 'border-[#496A52] text-[#496A52]'
                : 'border-transparent text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            Submit Observation
          </button>
          <button
            onClick={() => setActiveTab('list')}
            className={`pb-1.5 border-b-2 transition font-semibold ${
              activeTab === 'list'
                ? 'border-[#496A52] text-[#496A52]'
                : 'border-transparent text-[#5F665F] hover:text-[#20251F]'
            }`}
          >
            Report Queue ({recentReports.length})
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-3.5 overflow-y-auto space-y-3 flex-1 text-xs">
          {activeTab === 'submit' ? (
            <form onSubmit={handleSubmit} className="space-y-3">
              {successMsg && (
                <div className="p-2.5 rounded bg-[#EDF3EE] border border-[#C8D8CB] text-[#496A52] text-xs flex items-center gap-2 font-mono">
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  {successMsg}
                </div>
              )}

              {errorMsg && (
                <div className="p-2.5 rounded bg-[#FBF0F0] border border-[#E8B8B8] text-[#A83F3F] text-xs flex items-center gap-2 font-mono">
                  <AlertOctagon className="w-4 h-4 flex-shrink-0" />
                  {errorMsg}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] font-mono font-semibold text-[#5F665F] block mb-1">
                    OBSERVATION CATEGORY
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded p-1.5 focus:border-[#496A52] focus:outline-none font-mono"
                  >
                    <option value="VISIBLE_CRACK">Visible Tension Crack on Slope</option>
                    <option value="ROCKFALL">Rockfall / Talus Debris Slip</option>
                    <option value="ROAD_BLOCKAGE">Highway / Road Blockage</option>
                    <option value="WATER_SEEPAGE">Water Seepage / Scour</option>
                    <option value="SOIL_SUBSIDENCE">Soil Subsidence / Creep</option>
                    <option value="RETAINING_WALL_DAMAGE">Retaining Wall Damage</option>
                    <option value="ACTIVE_SLIDE">Active Mass Movement Slide</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-mono font-semibold text-[#5F665F] block mb-1">
                    OBSERVED SEVERITY
                  </label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="w-full bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded p-1.5 focus:border-[#496A52] focus:outline-none font-mono font-semibold"
                  >
                    <option value="Low">Low (Minor Spalling / Seepage)</option>
                    <option value="Moderate">Moderate (Visible Cracks &lt; 5cm)</option>
                    <option value="High">High (Active Displacement &gt; 5cm)</option>
                    <option value="Critical">Critical (Imminent Slope Collapse)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] font-mono font-semibold text-[#5F665F] block mb-1">LATITUDE (°N)</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={latitude}
                    onChange={(e) => setLatitude(parseFloat(e.target.value))}
                    className="w-full bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded p-1.5 font-mono focus:border-[#496A52] focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="text-[10px] font-mono font-semibold text-[#5F665F] block mb-1">LONGITUDE (°E)</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={longitude}
                    onChange={(e) => setLongitude(parseFloat(e.target.value))}
                    className="w-full bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded p-1.5 font-mono focus:border-[#496A52] focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-mono font-semibold text-[#5F665F] block mb-1">
                  DESCRIPTION & FIELD DETAILS
                </label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe slope fissure length, depth, water accumulation, proximity to highway..."
                  className="w-full bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded p-2 focus:border-[#496A52] focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] font-mono font-semibold text-[#5F665F] block mb-1">REPORTER NAME</label>
                  <input
                    type="text"
                    value={reporterName}
                    onChange={(e) => setReporterName(e.target.value)}
                    placeholder="e.g. Officer R. Sharma"
                    className="w-full bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded p-1.5 focus:border-[#496A52] focus:outline-none font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-mono font-semibold text-[#5F665F] block mb-1">REPORTER ROLE</label>
                  <select
                    value={reporterRole}
                    onChange={(e) => setReporterRole(e.target.value)}
                    className="w-full bg-[#FAF9F5] border border-[#D5D2C8] text-[#20251F] text-xs rounded p-1.5 focus:border-[#496A52] focus:outline-none font-mono"
                  >
                    <option value="field_officer">Field Officer (SDRF / DDMA)</option>
                    <option value="geologist">Geologist / GSI Staff</option>
                    <option value="ddma_staff">DDMA Disaster Response Staff</option>
                    <option value="citizen">Local Community Volunteer / Citizen</option>
                  </select>
                </div>
              </div>

              <div className="pt-0.5">
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-2 bg-[#17201B] hover:bg-[#222D26] text-[#FAF9F5] font-bold rounded text-xs transition flex items-center justify-center gap-2 disabled:opacity-50 font-mono"
                >
                  {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                  {submitting ? 'Submitting...' : 'Transmit Field Report'}
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-2">
              {loadingReports ? (
                <div className="py-10 flex justify-center text-[#5F665F] font-mono text-xs">
                  <Loader2 className="w-5 h-5 animate-spin text-[#496A52]" />
                </div>
              ) : recentReports.length > 0 ? (
                recentReports.map((r: any) => (
                  <div
                    key={r.id || r.report_id}
                    className="p-2.5 rounded bg-[#FAF9F5] border border-[#D5D2C8] space-y-1 font-mono"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-[#20251F] font-sans">
                          {r.location_name || `${r.district}, ${r.state}`}
                        </span>
                        <span className="text-[10px] text-[#5F665F]">
                          {r.observation_category}
                        </span>
                      </div>
                      <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-[#EDF3EE] text-[#496A52] border border-[#C8D8CB] uppercase">
                        {r.verification_status || 'submitted'}
                      </span>
                    </div>

                    <p className="text-xs text-[#20251F] leading-relaxed font-sans">{r.description}</p>

                    <div className="flex items-center justify-between text-[10px] text-[#889087] pt-1 border-t border-[#E2DFD5]">
                      <span>Reported by {r.reporter_name} ({r.reporter_role})</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Recent'}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-[#889087] text-xs font-mono">
                  No field ground-truth reports submitted yet.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-[#D5D2C8] bg-[#E9E6DD] flex items-center justify-between text-xs font-mono">
          <span className="text-[10px] text-[#5F665F]">
            DDMA Field Verification Triaging Protocol
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
