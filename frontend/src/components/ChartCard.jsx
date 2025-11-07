import React, { useState, useEffect } from "react";

export default function ChartCard({ title, endpoint, type }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
  }, [endpoint]);

  if (type === "plotly_html") {
    // For Plotly HTML endpoints from backend, use iframe
    return (
      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 overflow-hidden border border-gray-200" style={{ height: "600px", display: "flex", flexDirection: "column" }}>
        <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-base font-semibold text-gray-800 leading-tight">{title}</h2>
        </div>
        <div className="flex-1 relative bg-white" style={{ height: "550px", minHeight: "550px" }}>
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
                <p className="text-sm text-gray-500">Loading chart...</p>
              </div>
            </div>
          )}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
              <div className="text-center text-red-500">
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}
          <iframe
            src={endpoint}
            className="w-full h-full border-0"
            title={title}
            onLoad={() => {
              setLoading(false);
            }}
            style={{ 
              display: error ? "none" : "block",
              width: "100%",
              height: "100%"
            }}
          />
        </div>
      </div>
    );
  } else if (type === "png") {
    // For PNG image endpoints from backend
    return (
      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 overflow-hidden border border-gray-200" style={{ height: "600px", display: "flex", flexDirection: "column" }}>
        <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-base font-semibold text-gray-800 leading-tight">{title}</h2>
        </div>
        <div className="flex-1 relative bg-white flex items-center justify-center p-4" style={{ height: "550px", minHeight: "550px" }}>
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
                <p className="text-sm text-gray-500">Loading chart...</p>
              </div>
            </div>
          )}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
              <div className="text-center text-red-500">
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}
          <img
            src={endpoint}
            alt={title}
            className="max-w-full max-h-full object-contain"
            onLoad={() => {
              setLoading(false);
            }}
            onError={() => {
              setLoading(false);
              setError("Failed to load image");
            }}
            style={{ 
              display: loading || error ? "none" : "block",
              maxWidth: "100%",
              maxHeight: "100%"
            }}
          />
        </div>
      </div>
    );
  }

  return null;
}
