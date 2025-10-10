import React from "react";
import Plot from "react-plotly.js";

export default function ChartCard({ title, data }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-4 mb-6">
      <h2 className="text-lg font-semibold mb-2">{title}</h2>
      <Plot data={data.data} layout={data.layout} style={{ width: "100%" }} />
    </div>
  );
}
