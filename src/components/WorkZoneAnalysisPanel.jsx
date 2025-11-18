import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, Radio, X, Upload, Loader } from 'lucide-react';
import { getRiskColor, getRiskLabel, generateV2XAlert } from '../utils/riskUtils';
import { analyzeWorkZoneImage, formatWorkZoneForDashboard } from '../services/geminiVision';
import { useV2X } from '../contexts/V2XContext';

const WorkZoneAnalysisPanel = ({ workZone, onClose }) => {
  const [uploading, setUploading] = useState(false);
  const [aiWorkZone, setAiWorkZone] = useState(null);
  const [error, setError] = useState(null);

  // Get V2X context for broadcast registration
  const { registerBroadcast } = useV2X();

  // Use AI-analyzed work zone if available, otherwise use mock data
  const displayWorkZone = aiWorkZone || workZone;

  if (!displayWorkZone) return null;

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      // Call Gemini Vision API
      const analysis = await analyzeWorkZoneImage(file);

      if (analysis.error) {
        setError(analysis.message);
        setUploading(false);
        return;
      }

      // Format for dashboard display (now async - broadcasts to vRSU)
      const newWorkZone = await formatWorkZoneForDashboard(
        analysis,
        displayWorkZone.cameraId || 'UPLOAD',
        { lat: displayWorkZone.lat || 43.3850, lon: displayWorkZone.lon || -79.7400 },
        registerBroadcast // Pass V2X broadcast registration callback
      );

      // If no work zone detected, show message
      if (!newWorkZone) {
        setError('No work zone detected in this image. Please upload an image showing an active construction work zone.');
        setUploading(false);
        return;
      }

      setAiWorkZone(newWorkZone);
      setUploading(false);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to analyze image. Please try again.');
      setUploading(false);
    }
  };

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

      {/* NEW: AI Image Upload */}
      <div className="mb-4 p-4 bg-indigo-900/30 border border-indigo-600 rounded-lg">
        <div className="flex items-center mb-2">
          <Upload className="w-4 h-4 mr-2 text-indigo-300" />
          <h5 className="font-bold text-indigo-200">AI Analysis (Gemini Vision)</h5>
        </div>
        <p className="text-xs text-indigo-300 mb-3">
          Upload a work zone image for real-time AI safety analysis
        </p>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          disabled={uploading}
          className="block w-full text-sm text-gray-300
            file:mr-4 file:py-2 file:px-4
            file:rounded file:border-0
            file:text-sm file:font-semibold
            file:bg-indigo-600 file:text-white
            hover:file:bg-indigo-700
            file:cursor-pointer
            cursor-pointer"
        />
        {uploading && (
          <div className="flex items-center mt-2 text-sm text-indigo-300">
            <Loader className="w-4 h-4 mr-2 animate-spin" />
            Analyzing with Gemini AI...
          </div>
        )}
        {error && (
          <div className="mt-2 text-sm text-red-400">
            ⚠️ {error}
          </div>
        )}
        {aiWorkZone && (
          <>
            <div className="mt-2 text-sm text-green-400">
              ✅ AI Analysis Complete! Confidence: {(aiWorkZone.confidence * 100).toFixed(0)}%
            </div>
            {aiWorkZone.vrsuBroadcast && aiWorkZone.vrsuBroadcast.success && (
              <div className="mt-1 text-sm text-cyan-400">
                📡 vRSU Broadcast: {aiWorkZone.vrsuBroadcast.messageType} message sent
              </div>
            )}
            {aiWorkZone.vrsuBroadcast && !aiWorkZone.vrsuBroadcast.success && (
              <div className="mt-1 text-sm text-yellow-400">
                ⚠️ vRSU: {aiWorkZone.vrsuBroadcast.error}
              </div>
            )}
          </>
        )}
      </div>

      <div className="space-y-4">
        {/* Work Zone Name */}
        <div>
          <h4 className="font-bold text-white">{displayWorkZone.name || 'Uploaded Work Zone'}</h4>
          <p className="text-sm text-gray-400">
            {aiWorkZone ? '🤖 AI-Analyzed' : '📋 Mock Data'} | Camera: {displayWorkZone.cameraId || 'UPLOAD'}
          </p>
        </div>

        {/* Risk Score - Reused component */}
        <div className={`p-4 rounded-lg border-2 ${getRiskColor(displayWorkZone.riskScore)}`}>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold">RISK SCORE</span>
            <span className="text-3xl font-bold">{displayWorkZone.riskScore}/10</span>
          </div>
          <div className="text-sm font-semibold mt-2">
            {getRiskLabel(displayWorkZone.riskScore)}
          </div>
        </div>

        {/* Detection Stats - Reused grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-blue-900/30 border border-blue-600 p-3 rounded">
            <div className="text-sm text-blue-300 font-semibold">Workers</div>
            <div className="text-2xl font-bold text-blue-100">{displayWorkZone.workers || 0}</div>
          </div>
          <div className="bg-purple-900/30 border border-purple-600 p-3 rounded">
            <div className="text-sm text-purple-300 font-semibold">Vehicles</div>
            <div className="text-2xl font-bold text-purple-100">{displayWorkZone.vehicles || 0}</div>
          </div>
          <div className="bg-orange-900/30 border border-orange-600 p-3 rounded">
            <div className="text-sm text-orange-300 font-semibold">Equipment</div>
            <div className="text-2xl font-bold text-orange-100">{displayWorkZone.equipment || 0}</div>
          </div>
          <div className={`p-3 rounded border ${displayWorkZone.barriers ? 'bg-green-900/30 border-green-600' : 'bg-red-900/30 border-red-600'}`}>
            <div className={`text-sm font-semibold ${displayWorkZone.barriers ? 'text-green-300' : 'text-red-300'}`}>
              Barriers
            </div>
            <div className={`text-2xl font-bold ${displayWorkZone.barriers ? 'text-green-100' : 'text-red-100'}`}>
              {displayWorkZone.barriers ? 'YES' : 'NO'}
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
            {(displayWorkZone.hazards || []).map((hazard, idx) => (
              <li key={idx} className="text-sm text-red-300">• {hazard}</li>
            ))}
          </ul>
        </div>

        {/* MTO Compliance */}
        <div className={`p-4 rounded-lg border ${
          displayWorkZone.riskScore <= 3 ? 'bg-green-900/30 border-green-600' :
          displayWorkZone.riskScore <= 6 ? 'bg-yellow-900/30 border-yellow-600' :
          'bg-red-900/30 border-red-600'
        }`}>
          <h5 className="font-bold mb-2 flex items-center">
            <CheckCircle className="w-4 h-4 mr-2" />
            MTO BOOK 7 Compliance
          </h5>
          <div className="text-sm font-semibold mb-2">
            {displayWorkZone.mtoBookCompliance !== undefined
              ? (displayWorkZone.mtoBookCompliance ? 'COMPLIANT' : 'NON-COMPLIANT')
              : (displayWorkZone.riskScore <= 3 ? 'COMPLIANT' :
                 displayWorkZone.riskScore <= 6 ? 'PARTIAL COMPLIANCE' :
                 'NON-COMPLIANT')}
          </div>
          {displayWorkZone.violations && displayWorkZone.violations.length > 0 && (
            <ul className="text-sm space-y-1">
              {displayWorkZone.violations.map((violation, idx) => (
                <li key={idx}>• {violation}</li>
              ))}
            </ul>
          )}
          {!displayWorkZone.violations && displayWorkZone.riskScore > 6 && (
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
            {displayWorkZone.recommendations && displayWorkZone.recommendations.length > 0 ? (
              displayWorkZone.recommendations.map((rec, idx) => (
                <li key={idx} className="text-sm text-indigo-300">{idx + 1}. {rec}</li>
              ))
            ) : (
              <>
                {displayWorkZone.riskScore >= 7 && (
                  <>
                    <li className="text-sm text-indigo-300">1. IMMEDIATE: Close adjacent lane</li>
                    <li className="text-sm text-indigo-300">2. Deploy advance warning signs 500m upstream</li>
                    <li className="text-sm text-indigo-300">3. Install temporary barriers</li>
                    <li className="text-sm text-indigo-300">4. Reduce speed limit to 60 km/h</li>
                  </>
                )}
                {displayWorkZone.riskScore >= 4 && displayWorkZone.riskScore < 7 && (
                  <>
                    <li className="text-sm text-indigo-300">1. Add secondary barrier row</li>
                    <li className="text-sm text-indigo-300">2. Increase visibility signage</li>
                    <li className="text-sm text-indigo-300">3. Monitor traffic speeds</li>
                  </>
                )}
                {displayWorkZone.riskScore < 4 && (
                  <>
                    <li className="text-sm text-indigo-300">1. Continue current safety protocols</li>
                    <li className="text-sm text-indigo-300">2. Regular monitoring recommended</li>
                  </>
                )}
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
            {displayWorkZone.v2xAlert
              ? JSON.stringify(displayWorkZone.v2xAlert, null, 2)
              : generateV2XAlert(displayWorkZone.riskScore, displayWorkZone.hazards || [])}
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
