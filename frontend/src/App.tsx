import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { OverviewDashboard } from './components/dashboard/OverviewDashboard';
import { LandslideRiskMap } from './components/maps/LandslideRiskMap';
import { LiveMonitoringStation } from './components/monitoring/LiveMonitoringStation';
import { AlertsCenter } from './components/alerts/AlertsCenter';
import { ModelRegistryView } from './components/models/ModelRegistryView';
import { DataSourcesView } from './components/telemetry/DataSourcesView';
import {
  AlertRecord,
  Location,
  MapFeatureProperty,
  SystemHealth,
} from './types';
import { api } from './services/api';
import { Loader2 } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [mapFeatures, setMapFeatures] = useState<MapFeatureProperty[]>([]);
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [selectedStationId, setSelectedStationId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const loadInitialData = async () => {
    try {
      const [resLoc, resMap, resAlerts, resHealth] = await Promise.all([
        api.getLocations(),
        api.getMapRiskLayer(),
        api.getAlerts(),
        api.getHealth(),
      ]);

      setLocations(resLoc.items);
      const featureProps = resMap.features.map((f) => ({
        ...f.properties,
        latitude: f.geometry.coordinates[1],
        longitude: f.geometry.coordinates[0],
      }));
      setMapFeatures(featureProps);
      setAlerts(resAlerts.items);
      setSystemHealth(resHealth);

      if (resLoc.items.length > 0 && !selectedStationId) {
        setSelectedStationId(resLoc.items[0].id);
      }
    } catch (err) {
      console.error('Failed to load application data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleManualRefresh = () => {
    setRefreshing(true);
    loadInitialData();
  };

  useEffect(() => {
    loadInitialData();
    const interval = setInterval(async () => {
      try {
        const h = await api.getHealth();
        setSystemHealth(h);
      } catch (e) {}
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleInspectStation = (locationId: string) => {
    setSelectedStationId(locationId);
    setActiveTab('monitoring');
  };

  const activeAlerts = alerts.filter((a) => a.status === 'active');

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F4F1EA] flex flex-col items-center justify-center text-[#20251F] space-y-3 font-mono">
        <Loader2 className="w-8 h-8 animate-spin text-[#496A52]" />
        <div className="text-center">
          <h2 className="text-xs font-bold tracking-tight text-[#20251F]">NER LANDSLIDE EARLY WARNING</h2>
          <p className="text-[11px] text-[#5F665F] mt-0.5">Initializing Geospatial Threat Matrix...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F4F1EA] text-[#20251F] flex">
      {/* Persistent Left Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        activeAlertCount={activeAlerts.length}
        systemHealth={systemHealth}
      />

      {/* Main Content Viewport */}
      <div
        className={`flex-1 flex flex-col transition-all duration-150 ${
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        }`}
      >
        {/* Contextual Top Operations Header */}
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          systemHealth={systemHealth}
          activeAlertCount={activeAlerts.length}
          locations={locations}
          selectedStationId={selectedStationId}
          onSelectStation={(id) => setSelectedStationId(id)}
          onRefreshData={handleManualRefresh}
          refreshing={refreshing}
        />

        {/* Dynamic Page Views */}
        <main className="flex-1 p-4 sm:p-5 max-w-[1600px] w-full mx-auto">
          {activeTab === 'dashboard' && (
            <OverviewDashboard
              locations={locations}
              mapFeatures={mapFeatures}
              activeAlerts={activeAlerts}
              selectedStationId={selectedStationId}
              onSelectStation={(id) => setSelectedStationId(id)}
              onNavigateTab={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'map' && (
            <LandslideRiskMap
              features={mapFeatures}
              selectedStationId={selectedStationId}
              onSelectStation={(id) => setSelectedStationId(id)}
              onInspectStation={handleInspectStation}
            />
          )}

          {activeTab === 'monitoring' && (
            <LiveMonitoringStation
              locations={locations}
              selectedLocationId={selectedStationId}
              onSelectLocation={(id) => setSelectedStationId(id)}
            />
          )}

          {activeTab === 'alerts' && (
            <AlertsCenter
              alerts={alerts}
              onRefreshAlerts={loadInitialData}
              onInspectStation={handleInspectStation}
            />
          )}

          {activeTab === 'models' && <ModelRegistryView />}

          {activeTab === 'datasources' && <DataSourcesView systemHealth={systemHealth} />}
        </main>

        {/* Technical Operations Footer */}
        <footer className="border-t border-[#D5D2C8] bg-[#FAF9F5] py-2.5 px-6 text-center text-[10px] text-[#5F665F] font-mono">
          SIH 2026 Problem Statement 26001 &bull; Ministry of Development of North Eastern Region &bull; FastAPI, XGBoost M1/M2, GEE & Sentinel Remote Sensing
        </footer>
      </div>
    </div>
  );
}

export default App;
