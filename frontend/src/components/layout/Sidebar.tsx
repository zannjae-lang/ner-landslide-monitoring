import React from 'react';
import {
  Activity,
  Layers,
  MapPin,
  Bell,
  Cpu,
  Database,
  Radio,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { SystemHealth } from '../../types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  activeAlertCount: number;
  systemHealth: SystemHealth | null;
}

interface NavSection {
  title: string;
  items: {
    id: string;
    label: string;
    icon: React.ElementType;
    badge?: number;
    badgeColor?: string;
  }[];
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
  activeAlertCount,
  systemHealth,
}) => {
  const navSections: NavSection[] = [
    {
      title: 'COMMAND',
      items: [
        { id: 'dashboard', label: 'Regional Overview', icon: Activity },
      ],
    },
    {
      title: 'MONITORING',
      items: [
        { id: 'map', label: '8-State GIS Risk Map', icon: Layers },
        { id: 'monitoring', label: 'Station Telemetry', icon: MapPin },
      ],
    },
    {
      title: 'OPERATIONS',
      items: [
        {
          id: 'alerts',
          label: 'Alert Operations',
          icon: Bell,
          badge: activeAlertCount,
          badgeColor: 'bg-[#A83F3F] text-[#FAF9F5]',
        },
      ],
    },
    {
      title: 'INTELLIGENCE & AI',
      items: [
        { id: 'models', label: 'Model Registry (M1 & M2)', icon: Cpu },
        { id: 'datasources', label: 'Data Pipelines & Health', icon: Database },
      ],
    },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 h-screen bg-[#17201B] border-r border-[#2E3A33] z-40 flex flex-col justify-between transition-all duration-150 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="h-14 border-b border-[#2E3A33] px-3.5 flex items-center justify-between bg-[#17201B]">
          {!collapsed ? (
            <div
              className="flex items-center gap-2.5 cursor-pointer select-none"
              onClick={() => setActiveTab('dashboard')}
            >
              <div className="w-7 h-7 rounded bg-[#222D26] border border-[#2E3A33] flex items-center justify-center text-[#E8E5DC] font-bold text-xs">
                <Radio className="w-4 h-4 text-[#806B52]" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold tracking-tight text-[#E8E5DC]">NER LANDSLIDE</span>
                  <span className="text-[9px] font-mono font-bold px-1 py-0.2 rounded bg-[#222D26] text-[#AEB4AA] border border-[#2E3A33]">
                    OPS
                  </span>
                </div>
                <p className="text-[9px] text-[#AEB4AA] font-mono">MDoNER &bull; SIH 26001</p>
              </div>
            </div>
          ) : (
            <div
              className="mx-auto cursor-pointer"
              onClick={() => setActiveTab('dashboard')}
              title="NER Landslide Early Warning"
            >
              <div className="w-8 h-8 rounded bg-[#222D26] border border-[#2E3A33] flex items-center justify-center text-[#E8E5DC]">
                <Radio className="w-4 h-4 text-[#806B52]" />
              </div>
            </div>
          )}

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 rounded text-[#AEB4AA] hover:text-[#E8E5DC] hover:bg-[#222D26] transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Sections */}
        <nav className="p-2 space-y-3.5 overflow-y-auto max-h-[calc(100vh-120px)]">
          {navSections.map((section) => (
            <div key={section.title} className="space-y-1">
              {!collapsed && (
                <div className="px-2.5 py-0.5 text-[10px] font-mono font-bold text-[#AEB4AA] tracking-wider opacity-75">
                  {section.title}
                </div>
              )}
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center ${
                      collapsed ? 'justify-center px-0' : 'justify-between px-2.5'
                    } py-2 rounded text-xs font-medium transition-all relative ${
                      isActive
                        ? 'bg-[#222D26] text-[#E8E5DC] font-semibold'
                        : 'text-[#AEB4AA] hover:text-[#E8E5DC] hover:bg-[#222D26]/60'
                    }`}
                    title={collapsed ? item.label : undefined}
                  >
                    {isActive && !collapsed && (
                      <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r bg-[#496A52]" />
                    )}

                    <div className="flex items-center gap-2.5">
                      <Icon
                        className={`w-4 h-4 flex-shrink-0 ${
                          isActive ? 'text-[#E8E5DC]' : 'text-[#AEB4AA]'
                        }`}
                      />
                      {!collapsed && <span>{item.label}</span>}
                    </div>

                    {!collapsed && item.badge !== undefined && item.badge > 0 && (
                      <span
                        className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded ${
                          item.badgeColor || 'bg-[#222D26] text-[#E8E5DC]'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
      </div>

      {/* Sidebar Footer System Health */}
      <div className="p-3 border-t border-[#2E3A33] bg-[#17201B] text-[11px] font-mono">
        {!collapsed ? (
          <div className="flex items-center justify-between text-[#AEB4AA]">
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  systemHealth?.model_readiness ? 'bg-[#5C7A61]' : 'bg-[#B18A3A]'
                }`}
              />
              <span className="text-[#E8E5DC] text-[10px]">
                {systemHealth?.model_readiness ? 'MODELS READY' : 'INIT'}
              </span>
            </div>
            <span className="text-[10px] text-[#AEB4AA]">FastAPI</span>
          </div>
        ) : (
          <div className="flex justify-center" title="Model Status">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                systemHealth?.model_readiness ? 'bg-[#5C7A61]' : 'bg-[#B18A3A]'
              }`}
            />
          </div>
        )}
      </div>
    </aside>
  );
};
