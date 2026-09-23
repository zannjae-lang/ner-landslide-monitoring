import axios from 'axios';
import {
  AlertRecord,
  DataSourceStatus,
  Location,
  MapGeoJSONResponse,
  RiskEngineResult,
  SystemHealth,
} from '../types';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api/v1` : '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for satellite computations
});

export const api = {
  // Health & Model Status
  getHealth: async (): Promise<SystemHealth> => {
    const res = await apiClient.get<SystemHealth>('/health');
    return res.data;
  },

  getModelsStatus: async (): Promise<Record<string, any>> => {
    const res = await apiClient.get<Record<string, any>>('/models/status');
    return res.data;
  },

  // Locations
  getLocations: async (params?: { state?: string; district?: string; search?: string }): Promise<{ total: number; items: Location[] }> => {
    const res = await apiClient.get<{ total: number; items: Location[] }>('/locations', { params });
    return res.data;
  },

  getLocationById: async (locationId: string): Promise<Location> => {
    const res = await apiClient.get<Location>(`/locations/${locationId}`);
    return res.data;
  },

  // Predictions & Risk
  runPrediction: async (payload: {
    location_id?: string;
    latitude: number;
    longitude: number;
    state?: string;
    district?: string;
    location_name?: string;
    model1_features?: any;
    model2_features?: any;
  }): Promise<RiskEngineResult> => {
    const res = await apiClient.post<RiskEngineResult>('/predictions/run', payload);
    return res.data;
  },

  getLatestPrediction: async (locationId: string): Promise<RiskEngineResult> => {
    const res = await apiClient.get<RiskEngineResult>(`/predictions/latest/${locationId}`);
    return res.data;
  },

  getPredictionHistory: async (params?: {
    location_id?: string;
    state?: string;
    district?: string;
    risk_level?: string;
    limit?: number;
  }): Promise<{ total: number; items: any[] }> => {
    const res = await apiClient.get<{ total: number; items: any[] }>('/predictions/history', { params });
    return res.data;
  },

  // Weather & Telemetry
  getWeather: async (locationId: string): Promise<any> => {
    const res = await apiClient.get<any>(`/weather/${locationId}`);
    return res.data;
  },

  // Satellite Telemetry (Google Earth Engine)
  getSatelliteSummary: async (latitude: number, longitude: number): Promise<any> => {
    const res = await apiClient.get<any>('/satellite/summary', {
      params: { latitude, longitude },
    });
    return res.data;
  },

  // Alerts
  getAlerts: async (params?: {
    severity?: string;
    status?: string;
    state?: string;
  }): Promise<{ total: number; items: AlertRecord[] }> => {
    const res = await apiClient.get<{ total: number; items: AlertRecord[] }>('/alerts', { params });
    return res.data;
  },

  updateAlertStatus: async (
    alertId: string,
    status: 'active' | 'acknowledged' | 'resolved',
    notes?: string
  ): Promise<AlertRecord> => {
    const res = await apiClient.patch<AlertRecord>(`/alerts/${alertId}`, { status, notes });
    return res.data;
  },

  // Map Layer
  getMapRiskLayer: async (state?: string): Promise<MapGeoJSONResponse> => {
    const res = await apiClient.get<MapGeoJSONResponse>('/map/risk', {
      params: state ? { state } : undefined,
    });
    return res.data;
  },

  // Data Sources
  getDataSourcesStatus: async (): Promise<{ total: number; providers: DataSourceStatus[] }> => {
    const res = await apiClient.get<{ total: number; providers: DataSourceStatus[] }>('/data-sources/status');
    return res.data;
  },

  testProviderConnection: async (providerId: string): Promise<DataSourceStatus> => {
    const res = await apiClient.post<DataSourceStatus>(`/data-sources/providers/${providerId}/test`);
    return res.data;
  },

  // Satellite Analysis & Evidence (Phase 1 Isolated Satellite Foundation)
  getSatelliteMetadata: async (latitude: number, longitude: number, locationName?: string): Promise<any> => {
    const res = await apiClient.get<any>('/satellite-analysis/metadata', {
      params: { latitude, longitude, location_name: locationName },
    });
    return res.data;
  },

  getSentinel1Change: async (
    latitude: number,
    longitude: number,
    params?: { baseline_lookback_days?: number; recent_lookback_days?: number; location_name?: string }
  ): Promise<any> => {
    const res = await apiClient.get<any>('/satellite-analysis/sentinel1/change', {
      params: { latitude, longitude, ...params },
    });
    return res.data;
  },

  getSentinel2NDVI: async (
    latitude: number,
    longitude: number,
    params?: { baseline_lookback_days?: number; recent_lookback_days?: number; max_cloud_percent?: number; location_name?: string }
  ): Promise<any> => {
    const res = await apiClient.get<any>('/satellite-analysis/sentinel2/ndvi', {
      params: { latitude, longitude, ...params },
    });
    return res.data;
  },

  // Multi-Source Evidence Fusion
  evaluateEvidence: async (payload: {
    latitude: number;
    longitude: number;
    location_id?: string;
    location_name?: string;
    state?: string;
    district?: string;
    include_satellite_check?: boolean;
  }): Promise<any> => {
    const res = await apiClient.post<any>('/evidence/evaluate', payload);
    return res.data;
  },

  getStationEvidence: async (locationId: string): Promise<any> => {
    const res = await apiClient.get<any>(`/evidence/location/${locationId}`);
    return res.data;
  },

  // Spatial Grid & Regional Hotspots
  getRegionalHotspots: async (params?: { state?: string; min_lat?: number; max_lat?: number; min_lon?: number; max_lon?: number }): Promise<any> => {
    const res = await apiClient.get<any>('/spatial/hotspots', { params });
    return res.data;
  },

  getStatesSummary: async (): Promise<any> => {
    const res = await apiClient.get<any>('/spatial/states/summary');
    return res.data;
  },

  getDistrictRankings: async (): Promise<any> => {
    const res = await apiClient.get<any>('/spatial/district-rankings');
    return res.data;
  },

  // Infrastructure Exposure & Transport Corridors
  analyzeExposure: async (payload: {
    latitude: number;
    longitude: number;
    location_id?: string;
    location_name?: string;
    buffer_radius_meters?: number;
  }): Promise<any> => {
    const res = await apiClient.post<any>('/exposure/analyze', payload);
    return res.data;
  },

  getTransportCorridors: async (): Promise<any[]> => {
    const res = await apiClient.get<any[]>('/exposure/corridors');
    return res.data;
  },

  evaluateCorridorRisk: async (payload: {
    corridor_id?: string;
    corridor_name?: string;
    polyline_coordinates?: number[][];
    buffer_distance_meters?: number;
  }): Promise<any> => {
    const res = await apiClient.post<any>('/exposure/corridor-risk', payload);
    return res.data;
  },

  // Explainable AI Reports
  generateExplainableReport: async (payload: {
    latitude: number;
    longitude: number;
    location_id?: string;
    location_name?: string;
    state?: string;
    district?: string;
  }): Promise<any> => {
    const res = await apiClient.post<any>('/reports/generate', payload);
    return res.data;
  },

  getStationExplainableReport: async (locationId: string): Promise<any> => {
    const res = await apiClient.get<any>(`/reports/explain/location/${locationId}`);
    return res.data;
  },

  // Historical Disaster Replay
  getHistoricalEvents: async (): Promise<{ total_events: number; events: any[] }> => {
    const res = await apiClient.get<{ total_events: number; events: any[] }>('/replay/events');
    return res.data;
  },

  simulateHistoricalEvent: async (eventId: string): Promise<any> => {
    const res = await apiClient.post<any>(`/replay/simulate/${eventId}`);
    return res.data;
  },

  // Field Evidence & Citizen Reports
  submitFieldReport: async (payload: any): Promise<any> => {
    const res = await apiClient.post<any>('/field-reports', payload);
    return res.data;
  },

  getFieldReports: async (params?: { state?: string; district?: string; status?: string; category?: string }): Promise<any> => {
    const res = await apiClient.get<any>('/field-reports', { params });
    return res.data;
  },

  updateFieldReportStatus: async (reportId: string, payload: { verification_status: string; reviewer_notes?: string; reviewed_by?: string }): Promise<any> => {
    const res = await apiClient.patch<any>(`/field-reports/${reportId}`, payload);
    return res.data;
  },

  // System Observability & Telemetry
  getSystemTelemetry: async (): Promise<any> => {
    const res = await apiClient.get<any>('/monitoring/telemetry');
    return res.data;
  },
};


