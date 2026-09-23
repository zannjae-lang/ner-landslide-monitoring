export type RiskLevel = 'Normal' | 'Watch' | 'Alert' | 'Critical';
export type SusceptibilityClass = 'Very Low' | 'Low' | 'Moderate' | 'High' | 'Very High';
export type RainfallClass = 'Low' | 'Elevated' | 'High' | 'Critical';
export type DataQualityStatus = 'Fresh' | 'Stale' | 'Unavailable' | 'Provisional/Demo';

export interface Location {
  id: string;
  name: string;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  elevation_m?: number;
  slope_deg?: number;
  monitored: boolean;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Model1PredictionOutput {
  model_name: string;
  model_version: string;
  susceptibility_probability: number;
  susceptibility_percent: number;
  susceptibility_class: SusceptibilityClass;
  threshold: number;
  is_susceptible: boolean;
  operational_validation: boolean;
  calibrated: boolean;
  disclaimer: string;
}

export interface Model2PredictionOutput {
  model_name: string;
  model_version: string;
  dynamic_probability: number;
  warning_candidate: boolean;
  threshold: number;
  operational_validation: boolean;
  calibrated: boolean;
  data_timestamp: string;
  data_age_hours?: number;
  data_quality: DataQualityStatus;
  disclaimer: string;
}

export interface ComputerVisionOutput {
  module_name: string;
  status: string;
  evidence_probability?: number | null;
  is_operational: boolean;
  message: string;
}

export interface RiskEngineResult {
  engine_version: string;
  location_id?: string;
  location_name?: string;
  state?: string;
  district?: string;
  latitude?: number;
  longitude?: number;
  model1_result?: Model1PredictionOutput;
  model2_result?: Model2PredictionOutput;
  computer_vision_result?: ComputerVisionOutput;
  rainfall_24h_mm: number;
  rainfall_class: RainfallClass;
  rainfall_adjustment: number;
  combined_risk_score: number;
  final_risk: RiskLevel;
  data_status: DataQualityStatus;
  data_age_hours: number;
  is_stale: boolean;
  missing_fields: string[];
  warnings: string[];
  prediction_timestamp: string;
  prototype_warning: string;
  operational_validation: boolean;
}

export interface MapFeatureProperty {
  location_id: string;
  name: string;
  state: string;
  district: string;
  elevation_m?: number;
  slope_deg?: number;
  final_risk: RiskLevel;
  combined_risk_score: number;
  susceptibility_probability: number;
  susceptibility_class: SusceptibilityClass;
  dynamic_probability: number;
  warning_candidate: boolean;
  rainfall_24h_mm: number;
  rainfall_class: RainfallClass;
  data_status: DataQualityStatus;
  data_age_hours: number;
  is_stale: boolean;
  prototype_status: string;
}

export interface MapGeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number]; // [lon, lat]
  };
  properties: MapFeatureProperty;
}

export interface MapGeoJSONResponse {
  type: 'FeatureCollection';
  total: number;
  features: MapGeoJSONFeature[];
}

export interface AlertRecord {
  id: string;
  location_id: string;
  location_name: string;
  state: string;
  district: string;
  severity: RiskLevel;
  title: string;
  message: string;
  score: number;
  rainfall_24h_mm: number;
  status: 'active' | 'acknowledged' | 'resolved';
  source_prediction_id?: string;
  created_at: string;
  updated_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  audit_notes?: string;
}

export interface DataSourceStatus {
  provider_id: string;
  name: string;
  description: string;
  status: string;
  is_available: boolean;
  requires_auth: boolean;
  latency_ms?: number;
  last_successful_sync?: string;
  coverage: string;
  update_cadence: string;
  error_message?: string;
}

export interface SystemHealth {
  status: string;
  project: string;
  version: string;
  environment: string;
  uptime_seconds: number;
  timestamp_utc: string;
  database: string;
  model_readiness: boolean;
}
