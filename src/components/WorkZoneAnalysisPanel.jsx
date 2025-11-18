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
    <div className="p-3 bg-gray-900 border-t border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">Work Zone Details</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* NEW: AI Image Upload */}
      <div className="mb-3 p-2 bg-indigo-900/30 border border-indigo-600 rounded">
        <div className="flex items-center mb-1.5">
          <Upload className="w-3 h-3 mr-1.5 text-indigo-300" />
          <h5 className="text-xs font-bold text-indigo-200">AI Analysis (Gemini Vision)</h5>
        </div>
        <p className="text-[10px] text-indigo-300 mb-2 leading-tight">
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
          <div className="flex items-center mt-1.5 text-[10px] text-indigo-300">
            <Loader className="w-3 h-3 mr-1 animate-spin" />
            Analyzing with Gemini AI...
          </div>
        )}
        {error && (
          <div className="mt-1.5 text-[10px] text-red-400 leading-tight">
            ⚠️ {error}
          </div>
        )}
        {aiWorkZone && (
          <>
            <div className="mt-1.5 text-[10px] text-green-400">
              ✅ AI Analysis Complete! Confidence: {(aiWorkZone.confidence * 100).toFixed(0)}%
            </div>
            {aiWorkZone.vrsuBroadcast && aiWorkZone.vrsuBroadcast.success && (
              <div className="mt-0.5 text-[10px] text-cyan-400">
                📡 vRSU Broadcast: {aiWorkZone.vrsuBroadcast.messageType} message sent
              </div>
            )}
            {aiWorkZone.vrsuBroadcast && !aiWorkZone.vrsuBroadcast.success && (
              <div className="mt-0.5 text-[10px] text-yellow-400">
                ⚠️ vRSU: {aiWorkZone.vrsuBroadcast.error}
              </div>
            )}
          </>
        )}
      </div>

      <div className="space-y-2 mt-3">
        {/* Work Zone Name */}
        <div>
          <h4 className="text-sm font-bold text-white">{displayWorkZone.name || 'Uploaded Work Zone'}</h4>
          <p className="text-[10px] text-gray-400">
            {aiWorkZone ? '🤖 AI-Analyzed' : '📋 Mock Data'} | Camera: {displayWorkZone.cameraId || 'UPLOAD'}
          </p>
        </div>

        {/* Synthetic Test Badge */}
        {displayWorkZone.synthetic && displayWorkZone.syntheticMetadata && (
          <div className="p-2 bg-purple-900/30 border border-purple-600 rounded">
            <p className="text-xs font-bold text-purple-200">🧪 SYNTHETIC TEST</p>
            <p className="text-[9px] text-purple-300 mt-0.5">
              Image Source: {displayWorkZone.syntheticMetadata.photoSource}
            </p>
            <p className="text-[9px] text-purple-300">
              Photographer: {displayWorkZone.syntheticMetadata.photographer}
            </p>
            <p className="text-[9px] text-purple-300">
              Injected: {new Date(displayWorkZone.syntheticMetadata.injectedAt).toLocaleString()}
            </p>
            <p className="text-[9px] text-purple-400 mt-1">
              Search Terms: {displayWorkZone.syntheticMetadata.searchTerms}
            </p>
          </div>
        )}

        {/* Risk Score - Reused component */}
        <div className={`p-2 rounded border-2 ${getRiskColor(displayWorkZone.riskScore)}`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold">RISK SCORE</span>
            <span className="text-2xl font-bold">{displayWorkZone.riskScore}/10</span>
          </div>
          <div className="text-[10px] font-semibold mt-1">
            {getRiskLabel(displayWorkZone.riskScore)}
          </div>
        </div>

        {/* Detection Stats - Reused grid */}
        <div className="grid grid-cols-2 gap-1.5">
          <div className="bg-blue-900/30 border border-blue-600 p-1.5 rounded">
            <div className="text-[10px] text-blue-300 font-semibold">Workers</div>
            <div className="text-lg font-bold text-blue-100">{displayWorkZone.workers || 0}</div>
          </div>
          <div className="bg-purple-900/30 border border-purple-600 p-1.5 rounded">
            <div className="text-[10px] text-purple-300 font-semibold">Vehicles</div>
            <div className="text-lg font-bold text-purple-100">{displayWorkZone.vehicles || 0}</div>
          </div>
          <div className="bg-orange-900/30 border border-orange-600 p-1.5 rounded">
            <div className="text-[10px] text-orange-300 font-semibold">Equipment</div>
            <div className="text-lg font-bold text-orange-100">{displayWorkZone.equipment || 0}</div>
          </div>
          <div className={`p-1.5 rounded border ${displayWorkZone.barriers ? 'bg-green-900/30 border-green-600' : 'bg-red-900/30 border-red-600'}`}>
            <div className={`text-[10px] font-semibold ${displayWorkZone.barriers ? 'text-green-300' : 'text-red-300'}`}>
              Barriers
            </div>
            <div className={`text-lg font-bold ${displayWorkZone.barriers ? 'text-green-100' : 'text-red-100'}`}>
              {displayWorkZone.barriers ? 'YES' : 'NO'}
            </div>
          </div>
        </div>

        {/* Hazards - Reused component */}
        <div className="bg-red-900/30 border border-red-600 p-2 rounded">
          <h5 className="text-xs font-bold text-red-200 mb-1.5 flex items-center">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Identified Hazards
          </h5>
          <ul className="space-y-0.5">
            {(displayWorkZone.hazards || []).map((hazard, idx) => (
              <li key={idx} className="text-[10px] text-red-300 leading-tight">• {hazard}</li>
            ))}
          </ul>
        </div>

        {/* MTO Compliance */}
        <div className={`p-2 rounded border ${
          displayWorkZone.riskScore <= 3 ? 'bg-green-900/30 border-green-600' :
          displayWorkZone.riskScore <= 6 ? 'bg-yellow-900/30 border-yellow-600' :
          'bg-red-900/30 border-red-600'
        }`}>
          <h5 className="text-xs font-bold mb-1.5 flex items-center">
            <CheckCircle className="w-3 h-3 mr-1" />
            MTO BOOK 7 Compliance
          </h5>
          <div className="text-[10px] font-semibold mb-1.5">
            {displayWorkZone.mtoBookCompliance !== undefined
              ? (displayWorkZone.mtoBookCompliance ? 'COMPLIANT' : 'NON-COMPLIANT')
              : (displayWorkZone.riskScore <= 3 ? 'COMPLIANT' :
                 displayWorkZone.riskScore <= 6 ? 'PARTIAL COMPLIANCE' :
                 'NON-COMPLIANT')}
          </div>
          {displayWorkZone.violations && displayWorkZone.violations.length > 0 && (
            <ul className="text-[10px] space-y-0.5">
              {displayWorkZone.violations.map((violation, idx) => (
                <li key={idx} className="leading-tight">• {violation}</li>
              ))}
            </ul>
          )}
          {!displayWorkZone.violations && displayWorkZone.riskScore > 6 && (
            <p className="text-[10px] leading-tight">
              • BOOK 7 Section 3.2: Insufficient safety measures<br />
              • BOOK 7 Section 4.1: Missing or inadequate barriers
            </p>
          )}
        </div>

        {/* Recommendations */}
        <div className="bg-indigo-900/30 border border-indigo-600 p-2 rounded">
          <h5 className="text-xs font-bold text-indigo-200 mb-1.5">Recommended Actions</h5>
          <ul className="space-y-0.5">
            {displayWorkZone.recommendations && displayWorkZone.recommendations.length > 0 ? (
              displayWorkZone.recommendations.map((rec, idx) => (
                <li key={idx} className="text-[10px] text-indigo-300 leading-tight">{idx + 1}. {rec}</li>
              ))
            ) : (
              <>
                {displayWorkZone.riskScore >= 7 && (
                  <>
                    <li className="text-[10px] text-indigo-300 leading-tight">1. IMMEDIATE: Close adjacent lane</li>
                    <li className="text-[10px] text-indigo-300 leading-tight">2. Deploy advance warning signs 500m upstream</li>
                    <li className="text-[10px] text-indigo-300 leading-tight">3. Install temporary barriers</li>
                    <li className="text-[10px] text-indigo-300 leading-tight">4. Reduce speed limit to 60 km/h</li>
                  </>
                )}
                {displayWorkZone.riskScore >= 4 && displayWorkZone.riskScore < 7 && (
                  <>
                    <li className="text-[10px] text-indigo-300 leading-tight">1. Add secondary barrier row</li>
                    <li className="text-[10px] text-indigo-300 leading-tight">2. Increase visibility signage</li>
                    <li className="text-[10px] text-indigo-300 leading-tight">3. Monitor traffic speeds</li>
                  </>
                )}
                {displayWorkZone.riskScore < 4 && (
                  <>
                    <li className="text-[10px] text-indigo-300 leading-tight">1. Continue current safety protocols</li>
                    <li className="text-[10px] text-indigo-300 leading-tight">2. Regular monitoring recommended</li>
                  </>
                )}
              </>
            )}
          </ul>
        </div>

        {/* RSU Alert - Reused component */}
        <div className="bg-black text-green-400 p-2 rounded font-mono text-[10px] border border-gray-700">
          <div className="flex items-center mb-1.5">
            <Radio className="w-3 h-3 mr-1" />
            <span className="font-bold">V2X RSU BROADCAST</span>
          </div>
          <div className="bg-gray-900 p-1.5 rounded overflow-x-auto">
            {displayWorkZone.v2xAlert
              ? JSON.stringify(displayWorkZone.v2xAlert, null, 2)
              : generateV2XAlert(displayWorkZone.riskScore, displayWorkZone.hazards || [])}
          </div>
          <div className="text-[9px] text-gray-500 mt-1">
            SAE J2735 TIM Message Format | 1000m Range
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkZoneAnalysisPanel;
