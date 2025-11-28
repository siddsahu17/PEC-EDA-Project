import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

const PlotlyGraph = ({ endpoint, title }) => {
  const [data, setData] = useState(null);
  const [layout, setLayout] = useState(null);
  const [inference, setInference] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000${endpoint}`);
        if (response.data.error) {
          setError(response.data.error);
        } else {
          // Handle new response structure { graph: {...}, inference: "..." }
          const graphData = response.data.graph || response.data; // Fallback for old structure
          const inferenceText = response.data.inference || "";
          
          setData(graphData.data);
          setLayout(graphData.layout);
          setInference(inferenceText);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  if (loading) return <div className="glass-panel loading">Loading {title}...</div>;
  if (error) return <div className="glass-panel error">Error: {error}</div>;

  // Custom Dark Theme Layout Overrides
  const darkLayout = {
    ...layout,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#e2e8f0' },
    xaxis: { ...layout?.xaxis, gridcolor: '#334155' },
    yaxis: { ...layout?.yaxis, gridcolor: '#334155' },
    margin: { t: 40, r: 20, b: 40, l: 40 },
    autosize: true
  };

  return (
    <div className="glass-panel graph-container">
      <Plot
        data={data}
        layout={darkLayout}
        useResizeHandler={true}
        style={{ width: "100%", height: "100%" }}
        config={{ responsive: true, displayModeBar: false }}
      />
      {inference && (
        <div className="inference-box">
          <strong>Insight:</strong> {inference}
        </div>
      )}
    </div>
  );
};

export default PlotlyGraph;
