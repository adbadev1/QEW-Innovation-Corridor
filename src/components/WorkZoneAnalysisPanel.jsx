import React from 'react';
import { AlertTriangle, CheckCircle, Radio, X } from 'lucide-react';
import { getRiskColor, getRiskLabel, generateV2XAlert } from '../utils/riskUtils';

const WorkZoneAnalysisPanel = ({ workZone, onClose }) => {
  if (!workZone) return null;

  return (
    <div className="p-6 bg-gray-900 border-t border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Work Zone Details</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="space-y-4">
        {/* Work Zone Name */}
        <div>
          <h4 className="font-bold text-white">{workZone.name}</h4>
          <p className="text-sm text-gray-400">Camera: {workZone.cameraId}</p>
        </div>

        {/* Risk Score - Reused component */}
        <div className={`p-4 rounded-lg border-2 ${getRiskColor(workZone.riskScore)}`}>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold">RISK SCORE</span>
            <span className="text-3xl font-bold">{workZone.riskScore}/10</span>
          </div>
          <div className="text-sm font-semibold mt-2">
            {getRiskLabel(workZone.riskScore)}
          </div>
        </div>

        {/* Detection Stats - Reused grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-blue-900/30 border border-blue-600 p-3 rounded">
            <div className="text-sm text-blue-300 font-semibold">Workers</div>
            <div className="text-2xl font-bold text-blue-100">{workZone.workers}</div>
          </div>
          <div className="bg-purple-900/30 border border-purple-600 p-3 rounded">
            <div className="text-sm text-purple-300 font-semibold">Vehicles</div>
            <div className="text-2xl font-bold text-purple-100">{workZone.vehicles}</div>
          </div>
          <div className="bg-orange-900/30 border border-orange-600 p-3 rounded">
            <div className="text-sm text-orange-300 font-semibold">Equipment</div>
            <div className="text-2xl font-bold text-orange-100">{workZone.equipment}</div>
          </div>
          <div className={`p-3 rounded border ${workZone.barriers ? 'bg-green-900/30 border-green-600' : 'bg-red-900/30 border-red-600'}`}>
            <div className={`text-sm font-semibold ${workZone.barriers ? 'text-green-300' : 'text-red-300'}`}>
              Barriers
            </div>
            <div className={`text-2xl font-bold ${workZone.barriers ? 'text-green-100' : 'text-red-100'}`}>
              {workZone.barriers ? 'YES' : 'NO'}
            </div>
          </div>
        </div>

        {/* Hazards - Reused component */}
        <div className="bg-red-900/30 border border-red-600 p-4 rounded-lg">
          <h5 className="font-bold text-red-200 mb-2 flex items-center">
            <AlertTriangle className="w-4 h-4 mr-2" />
            Identified Hazards
          </h5>
          <ul className="space-y-1">
            {workZone.hazards.map((hazard, idx) => (
              <li key={idx} className="text-sm text-red-300">• {hazard}</li>
            ))}
          </ul>
        </div>

        {/* MTO Compliance */}
        <div className={`p-4 rounded-lg border ${
          workZone.riskScore <= 3 ? 'bg-green-900/30 border-green-600' :
          workZone.riskScore <= 6 ? 'bg-yellow-900/30 border-yellow-600' :
          'bg-red-900/30 border-red-600'
        }`}>
          <h5 className="font-bold mb-2 flex items-center">
            <CheckCircle className="w-4 h-4 mr-2" />
            MTO BOOK 7 Compliance
          </h5>
          <div className="text-sm font-semibold mb-2">
            {workZone.riskScore <= 3 ? 'COMPLIANT' :
             workZone.riskScore <= 6 ? 'PARTIAL COMPLIANCE' :
             'NON-COMPLIANT'}
          </div>
          {workZone.riskScore > 6 && (
            <p className="text-sm">
              • BOOK 7 Section 3.2: Insufficient safety measures<br />
              • BOOK 7 Section 4.1: Missing or inadequate barriers
            </p>
          )}
        </div>

        {/* Recommendations */}
        <div className="bg-indigo-900/30 border border-indigo-600 p-4 rounded-lg">
          <h5 className="font-bold text-indigo-200 mb-2">Recommended Actions</h5>
          <ul className="space-y-1">
            {workZone.riskScore >= 7 && (
              <>
                <li className="text-sm text-indigo-300">1. IMMEDIATE: Close adjacent lane</li>
                <li className="text-sm text-indigo-300">2. Deploy advance warning signs 500m upstream</li>
                <li className="text-sm text-indigo-300">3. Install temporary barriers</li>
                <li className="text-sm text-indigo-300">4. Reduce speed limit to 60 km/h</li>
              </>
            )}
            {workZone.riskScore >= 4 && workZone.riskScore < 7 && (
              <>
                <li className="text-sm text-indigo-300">1. Add secondary barrier row</li>
                <li className="text-sm text-indigo-300">2. Increase visibility signage</li>
                <li className="text-sm text-indigo-300">3. Monitor traffic speeds</li>
              </>
            )}
            {workZone.riskScore < 4 && (
              <>
                <li className="text-sm text-indigo-300">1. Continue current safety protocols</li>
                <li className="text-sm text-indigo-300">2. Regular monitoring recommended</li>
              </>
            )}
          </ul>
        </div>

        {/* RSU Alert - Reused component */}
        <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm border border-gray-700">
          <div className="flex items-center mb-2">
            <Radio className="w-4 h-4 mr-2" />
            <span className="font-bold">V2X RSU BROADCAST</span>
          </div>
          <div className="bg-gray-900 p-2 rounded">
            {generateV2XAlert(workZone.riskScore, workZone.hazards)}
          </div>
          <div className="text-xs text-gray-500 mt-2">
            SAE J2735 TIM Message Format | 1000m Range
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkZoneAnalysisPanel;
