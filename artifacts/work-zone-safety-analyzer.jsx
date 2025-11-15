import React, { useState } from 'react';
import { Upload, AlertTriangle, CheckCircle, Shield, Radio, FileText } from 'lucide-react';

const WorkZoneSafetyAnalyzer = () => {
  const [image, setImage] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedDemo, setSelectedDemo] = useState(null);

  // Demo scenarios with pre-loaded results
  const demoScenarios = [
    {
      id: 1,
      name: "QEW Work Zone - High Risk",
      imageUrl: "/api/placeholder/600/400",
      analysis: {
        riskScore: 8,
        workers: 4,
        vehicles: 2,
        equipment: 1,
        barriers: false,
        hazards: [
          "Workers within 2m of active traffic lane",
          "Approaching vehicle speed >80 km/h",
          "Missing advance warning signage",
          "No safety barriers deployed"
        ],
        compliance: {
          book7: "NON-COMPLIANT",
          violations: [
            "BOOK 7 Section 3.2: Insufficient lane closure distance",
            "BOOK 7 Section 4.1: Missing temporary barriers"
          ]
        },
        recommendations: [
          "IMMEDIATE: Close adjacent lane",
          "Deploy advance warning signs 500m upstream",
          "Install temporary concrete barriers",
          "Reduce speed limit to 60 km/h"
        ],
        rsuAlert: "WORK_ZONE_HAZARD|HIGH_RISK|WORKERS_PRESENT|REDUCE_SPEED_60"
      }
    },
    {
      id: 2,
      name: "QEW Work Zone - Medium Risk",
      imageUrl: "/api/placeholder/600/400",
      analysis: {
        riskScore: 5,
        workers: 2,
        vehicles: 1,
        equipment: 2,
        barriers: true,
        hazards: [
          "Equipment partially obstructing sight lines",
          "Single barrier configuration (double recommended)"
        ],
        compliance: {
          book7: "PARTIAL COMPLIANCE",
          violations: [
            "BOOK 7 Section 4.3: Barrier configuration suboptimal"
          ]
        },
        recommendations: [
          "Add secondary barrier row",
          "Relocate excavator 3m north",
          "Increase lighting for night operations"
        ],
        rsuAlert: "WORK_ZONE_ACTIVE|MEDIUM_RISK|REDUCE_SPEED_80"
      }
    },
    {
      id: 3,
      name: "QEW Work Zone - Low Risk",
      imageUrl: "/api/placeholder/600/400",
      analysis: {
        riskScore: 2,
        workers: 3,
        vehicles: 0,
        equipment: 1,
        barriers: true,
        hazards: [
          "Minor: Cones spaced 12m apart (10m recommended)"
        ],
        compliance: {
          book7: "COMPLIANT",
          violations: []
        },
        recommendations: [
          "Adjust cone spacing to 10m intervals",
          "Continue current safety protocols"
        ],
        rsuAlert: "WORK_ZONE_ACTIVE|LOW_RISK|PROCEED_WITH_CAUTION"
      }
    }
  ];

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result);
        analyzeImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDemoSelect = (scenario) => {
    setSelectedDemo(scenario);
    setImage(scenario.imageUrl);
    setAnalysis(scenario.analysis);
  };

  const analyzeImage = async (imageData) => {
    setLoading(true);

    // Simulate AI analysis (in real implementation, call Claude API)
    setTimeout(() => {
      // Mock analysis - replace with actual Claude Vision API call
      const mockAnalysis = {
        riskScore: Math.floor(Math.random() * 4) + 5,
        workers: Math.floor(Math.random() * 5) + 1,
        vehicles: Math.floor(Math.random() * 3),
        equipment: Math.floor(Math.random() * 3),
        barriers: Math.random() > 0.5,
        hazards: [
          "Detected workers near active lane",
          "Vehicle approaching at high speed",
          "Possible missing safety equipment"
        ],
        compliance: {
          book7: "UNDER REVIEW",
          violations: ["Analysis in progress"]
        },
        recommendations: [
          "Deploy additional safety measures",
          "Review barrier placement",
          "Enhance warning signage"
        ],
        rsuAlert: "WORK_ZONE_DETECTED|RISK_ASSESSMENT_PENDING"
      };

      setAnalysis(mockAnalysis);
      setLoading(false);
    }, 2000);
  };

  const getRiskColor = (score) => {
    if (score >= 7) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 4) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };

  const getRiskLabel = (score) => {
    if (score >= 7) return 'HIGH RISK';
    if (score >= 4) return 'MEDIUM RISK';
    return 'LOW RISK';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-12 h-12 text-indigo-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-800">
              AI Work Zone Safety Analyzer
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            QEW Innovation Corridor | OVIN Pilot Project
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Powered by Claude Vision AI + V2X Technology
          </p>
        </div>

        {/* Demo Scenarios */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            Quick Demo Scenarios
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {demoScenarios.map((scenario) => (
              <button
                key={scenario.id}
                onClick={() => handleDemoSelect(scenario)}
                className="p-4 border-2 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all text-left"
              >
                <div className="font-semibold text-gray-800">{scenario.name}</div>
                <div className={`text-sm mt-2 px-2 py-1 rounded inline-block ${getRiskColor(scenario.analysis.riskScore)}`}>
                  Risk: {scenario.analysis.riskScore}/10
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Image Upload */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <Upload className="w-6 h-6 mr-2" />
              Upload Work Zone Image
            </h2>

            <div className="border-4 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                {image ? (
                  <img src={image} alt="Work zone" className="max-w-full h-auto rounded-lg mx-auto" />
                ) : (
                  <div>
                    <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600 text-lg">Click to upload or drag image here</p>
                    <p className="text-gray-400 text-sm mt-2">Supports: JPG, PNG, WebP</p>
                  </div>
                )}
              </label>
            </div>

            {loading && (
              <div className="mt-4 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <p className="text-gray-600 mt-2">Analyzing work zone safety...</p>
              </div>
            )}
          </div>

          {/* Right Column: Analysis Results */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <AlertTriangle className="w-6 h-6 mr-2" />
              Safety Analysis
            </h2>

            {analysis ? (
              <div className="space-y-4">
                {/* Risk Score */}
                <div className={`p-4 rounded-lg border-2 ${getRiskColor(analysis.riskScore)}`}>
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold">RISK SCORE</span>
                    <span className="text-3xl font-bold">{analysis.riskScore}/10</span>
                  </div>
                  <div className="text-sm font-semibold mt-2">
                    {getRiskLabel(analysis.riskScore)}
                  </div>
                </div>

                {/* Detected Elements */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <div className="text-sm text-blue-600 font-semibold">Workers</div>
                    <div className="text-2xl font-bold text-blue-800">{analysis.workers}</div>
                  </div>
                  <div className="bg-purple-50 p-3 rounded border border-purple-200">
                    <div className="text-sm text-purple-600 font-semibold">Vehicles</div>
                    <div className="text-2xl font-bold text-purple-800">{analysis.vehicles}</div>
                  </div>
                  <div className="bg-orange-50 p-3 rounded border border-orange-200">
                    <div className="text-sm text-orange-600 font-semibold">Equipment</div>
                    <div className="text-2xl font-bold text-orange-800">{analysis.equipment}</div>
                  </div>
                  <div className={`p-3 rounded border ${analysis.barriers ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                    <div className={`text-sm font-semibold ${analysis.barriers ? 'text-green-600' : 'text-red-600'}`}>
                      Barriers
                    </div>
                    <div className={`text-2xl font-bold ${analysis.barriers ? 'text-green-800' : 'text-red-800'}`}>
                      {analysis.barriers ? 'YES' : 'NO'}
                    </div>
                  </div>
                </div>

                {/* Hazards */}
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <h3 className="font-bold text-red-800 mb-2 flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Identified Hazards
                  </h3>
                  <ul className="space-y-1">
                    {analysis.hazards.map((hazard, idx) => (
                      <li key={idx} className="text-sm text-red-700">• {hazard}</li>
                    ))}
                  </ul>
                </div>

                {/* MTO Compliance */}
                <div className={`p-4 rounded-lg border ${
                  analysis.compliance.book7 === 'COMPLIANT' ? 'bg-green-50 border-green-200' :
                  analysis.compliance.book7 === 'PARTIAL COMPLIANCE' ? 'bg-yellow-50 border-yellow-200' :
                  'bg-red-50 border-red-200'
                }`}>
                  <h3 className="font-bold mb-2 flex items-center">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    MTO BOOK 7 Compliance
                  </h3>
                  <div className="text-sm font-semibold mb-2">{analysis.compliance.book7}</div>
                  {analysis.compliance.violations.length > 0 && (
                    <ul className="space-y-1">
                      {analysis.compliance.violations.map((violation, idx) => (
                        <li key={idx} className="text-sm">• {violation}</li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Recommendations */}
                <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                  <h3 className="font-bold text-indigo-800 mb-2">Recommended Actions</h3>
                  <ul className="space-y-1">
                    {analysis.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-sm text-indigo-700">
                        {idx + 1}. {rec}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* RSU Alert */}
                <div className="bg-gray-800 text-green-400 p-4 rounded-lg font-mono text-sm">
                  <div className="flex items-center mb-2">
                    <Radio className="w-4 h-4 mr-2" />
                    <span className="font-bold">V2X RSU BROADCAST</span>
                  </div>
                  <div className="bg-black p-2 rounded">
                    {analysis.rsuAlert}
                  </div>
                  <div className="text-xs text-gray-400 mt-2">
                    SAE J2735 TIM Message Format | 1000m Range
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">
                <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Upload an image or select a demo scenario to begin analysis</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-600 text-sm">
          <p>QEW Innovation Corridor Pilot Project | ADBA Labs</p>
          <p className="mt-1">Applying for OVIN $150K Funding | Building the Future of Smart Highway Safety</p>
        </div>
      </div>
    </div>
  );
};

export default WorkZoneSafetyAnalyzer;
