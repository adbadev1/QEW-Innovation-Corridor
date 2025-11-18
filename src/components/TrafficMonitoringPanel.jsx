import React, { useState, useEffect } from 'react';
import { Activity, Radio, ChevronDown, ChevronUp, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

/**
 * Traffic Monitoring Panel - Collapsible Persistent Dropdown
 *
 * FEATURES:
 * - Persistent collapsible dropdown (always visible in right panel)
 * - AI Traffic Analyst with live analysis
 * - Active RSU Broadcasts display
 * - Traffic Flow chart (last 20 minutes)
 * - Expansion state persists across sessions
 */
function TrafficMonitoringPanel({ aiAnalysis, alerts, trafficData }) {
  const [isExpanded, setIsExpanded] = useState(() => {
    const saved = localStorage.getItem('trafficMonitoringExpanded');
    return saved === null ? true : saved === 'true'; // Default to expanded
  });

  // Persist expansion state
  useEffect(() => {
    localStorage.setItem('trafficMonitoringExpanded', isExpanded.toString());
  }, [isExpanded]);

  return (
    <div className="bg-gray-800 text-white border-b border-gray-700">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-2 bg-gradient-to-r from-green-600 to-teal-700 flex items-center justify-between hover:from-green-700 hover:to-teal-800 transition"
      >
        <div className="flex items-center space-x-1.5">
          <Activity className="w-4 h-4" />
          <div className="text-left">
            <h2 className="text-sm font-bold">Traffic Monitoring & Analysis</h2>
            <p className="text-[9px] text-green-100">
              {alerts.length > 0 ? `🔴 ${alerts.length} active alert${alerts.length > 1 ? 's' : ''}` : '🟢 No alerts'} • AI Analysis Active
            </p>
          </div>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="flex flex-col max-h-[600px]">

          {/* AI Traffic Analyst */}
          <div className="p-3 border-b border-gray-700">
            <h3 className="text-xs font-semibold mb-2 flex items-center">
              <Activity className="w-3 h-3 mr-1 text-indigo-400" />
              AI Traffic Analyst
            </h3>
            <div className="bg-gray-900 p-2 rounded border border-gray-700">
              <p className="text-xs text-gray-300 leading-tight">
                {aiAnalysis || "Initializing AI analysis..."}
              </p>
              <p className="text-[10px] text-gray-500 mt-1">
                Powered by Gemini 2.0 Flash
              </p>
            </div>
          </div>

          {/* Active RSU Broadcasts */}
          <div className="p-3 border-b border-gray-700">
            <h3 className="text-xs font-semibold mb-2 flex items-center">
              <Radio className="w-3 h-3 mr-1 text-red-400" />
              Active RSU Broadcasts
            </h3>
            <div className="space-y-1.5 max-h-40 overflow-y-auto">
              {alerts.length > 0 ? alerts.map(alert => (
                <div key={alert.id} className="bg-red-900/30 border border-red-600 p-2 rounded">
                  <p className="text-xs text-red-200 leading-tight">{alert.message}</p>
                  <p className="text-[10px] font-mono text-gray-400 mt-1 leading-tight">{alert.rsuAlert}</p>
                  <p className="text-[10px] text-gray-500 mt-0.5">{alert.timestamp}</p>
                </div>
              )) : (
                <p className="text-xs text-gray-500">No active alerts</p>
              )}
            </div>
          </div>

          {/* Traffic Flow Chart */}
          <div className="p-3 border-b border-gray-700">
            <h3 className="text-xs font-semibold mb-2 flex items-center">
              <TrendingUp className="w-3 h-3 mr-1 text-blue-400" />
              Traffic Flow (Last 20 min)
            </h3>
            <ResponsiveContainer width="100%" height={100}>
              <LineChart data={trafficData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" tick={{ fontSize: 8 }} />
                <YAxis stroke="#9CA3AF" tick={{ fontSize: 8 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', fontSize: '10px' }}
                  labelStyle={{ color: '#E5E7EB', fontSize: '10px' }}
                />
                <Line type="monotone" dataKey="avgSpeed" stroke="#3B82F6" strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Footer Info */}
          <div className="p-1.5 bg-gray-900 border-t border-gray-700 text-[9px] text-gray-500 text-center">
            Real-Time Traffic Monitoring • AI-Powered Analysis • V2X Alert Management
          </div>
        </div>
      )}
    </div>
  );
}

export default TrafficMonitoringPanel;
