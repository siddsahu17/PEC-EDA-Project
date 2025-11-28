import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import axios from 'axios';

const MLDashboard = () => {
  const [regMetrics, setRegMetrics] = useState(null);
  const [classMetrics, setClassMetrics] = useState(null);
  const [confusionMatrix, setConfusionMatrix] = useState(null);
  const [selectedModel, setSelectedModel] = useState("Random Forest");
  const [regPlot, setRegPlot] = useState(null);
  const [loadingPlot, setLoadingPlot] = useState(false);

  useEffect(() => {
    // Fetch Regression Metrics
    axios.get('http://127.0.0.1:8000/api/ml/regression/compare')
      .then(res => {
        setRegMetrics(res.data);
        // Set default model to the first available one if Linear Regression is missing
        if (res.data && Object.keys(res.data).length > 0) {
          const availableModels = Object.keys(res.data);
          if (!availableModels.includes("Linear Regression")) {
            setSelectedModel(availableModels[0]);
          }
        }
      })
      .catch(err => console.error("Error fetching regression metrics", err));

    // Fetch Classification Metrics
    axios.get('http://127.0.0.1:8000/api/ml/classification/metrics')
      .then(res => setClassMetrics(res.data))
      .catch(err => console.error("Error fetching class metrics", err));

    // Fetch Confusion Matrix
    axios.get('http://127.0.0.1:8000/api/ml/classification/confusion_matrix')
      .then(res => setConfusionMatrix(res.data))
      .catch(err => console.error("Error fetching CM", err));
  }, []);

  useEffect(() => {
    if (selectedModel) {
      setLoadingPlot(true);
      setRegPlot(null);
      setConfusionMatrix(null); // Reset CM
      
      // Fetch Plot
      axios.get(`http://127.0.0.1:8000/api/ml/regression/plot/${selectedModel}`)
        .then(res => {
          if (res.data && res.data.error) {
            console.warn(res.data.error);
            setRegPlot(null);
          } else {
            setRegPlot(res.data);
          }
        })
        .catch(err => console.error("Error fetching plot", err))
        .finally(() => setLoadingPlot(false));

      // Fetch Confusion Matrix (Binned for Regression)
      axios.get(`http://127.0.0.1:8000/api/ml/confusion_matrix/${selectedModel}`)
        .then(res => {
            if (!res.data.error) setConfusionMatrix(res.data);
        })
        .catch(err => console.error("Error fetching regression CM", err));
    }
  }, [selectedModel]);

  const renderConfusionMatrix = (cmData, title) => {
    if (!cmData || !cmData.matrix) return null;
    const { matrix, labels } = cmData;
    
    return (
      <div style={{ marginTop: '1rem', textAlign: 'center' }}>
        <h4 style={{ color: '#94a3b8', marginBottom: '10px' }}>{title}</h4>
        <div style={{ display: 'inline-grid', gridTemplateColumns: `auto repeat(${labels.length}, 1fr)`, gap: '5px' }}>
          {/* Header Row */}
          <div></div>
          {labels.map(l => <div key={l} style={{ color: '#38bdf8', fontWeight: 'bold', padding: '5px' }}>{l}</div>)}
          
          {/* Matrix Rows */}
          {matrix.map((row, i) => (
            <React.Fragment key={i}>
              <div style={{ color: '#38bdf8', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingRight: '10px' }}>{labels[i]}</div>
              {row.map((val, j) => (
                <div key={j} style={{ 
                  background: `rgba(56, 189, 248, ${Math.max(0.1, Math.min(val/500, 1))})`, 
                  color: val > 200 ? '#000' : '#fff',
                  padding: '15px', borderRadius: '4px', minWidth: '60px'
                }}>
                  {val}
                </div>
              ))}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  };

  // State for Classification CM separately
  const [classCM, setClassCM] = useState(null);

  useEffect(() => {
     // Fetch Classification CM
     axios.get('http://127.0.0.1:8000/api/ml/confusion_matrix/Status Classifier')
      .then(res => setClassCM(res.data))
      .catch(err => console.error("Error fetching class CM", err));
  }, []);

  return (
    <div className="ml-dashboard">
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#f1f5f9' }}>Machine Learning Models</h2>

      {/* Regression Comparison Section */}
      <div className="glass-panel" style={{ padding: '20px', marginBottom: '30px' }}>
        <h3 style={{ color: '#38bdf8', marginBottom: '20px' }}>Price Prediction Models (Regression)</h3>
        
        {/* Metrics Table */}
        <div style={{ overflowX: 'auto', marginBottom: '30px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', color: '#e2e8f0' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155' }}>
                <th style={{ padding: '12px', textAlign: 'left' }}>Model</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>R2 Score</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>MAE</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>MSE</th>
                <th style={{ padding: '12px', textAlign: 'left' }}>RMSE</th>
              </tr>
            </thead>
            <tbody>
              {regMetrics ? Object.entries(regMetrics).map(([name, m]) => (
                <tr key={name} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px', fontWeight: 'bold', color: '#38bdf8' }}>{name}</td>
                  <td style={{ padding: '12px' }}>{m["R2 Score"]}</td>
                  <td style={{ padding: '12px' }}>{m["MAE"]}</td>
                  <td style={{ padding: '12px' }}>{m["MSE"]}</td>
                  <td style={{ padding: '12px' }}>{m["RMSE"]}</td>
                </tr>
              )) : <tr><td colSpan="5" style={{ padding: '20px', textAlign: 'center' }}>Loading metrics...</td></tr>}
            </tbody>
          </table>
        </div>

        {/* Regression Plots & CM */}
        <div>
          {/* Model Title */}
          <div style={{ marginBottom: '20px', textAlign: 'center' }}>
             <h4 style={{ color: '#38bdf8', fontSize: '1.2rem' }}>Model: Random Forest Regressor</h4>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
            {/* Plot */}
            <div style={{ minHeight: '400px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', padding: '10px' }}>
                {loadingPlot ? (
                <div style={{ padding: '40px', textAlign: 'center' }}>Loading Plot...</div>
                ) : regPlot && regPlot.data ? (
                <Plot
                    data={regPlot.data}
                    layout={{
                    ...regPlot.layout,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: '#e2e8f0' },
                    title: { text: `${selectedModel}: Actual vs Predicted`, font: { color: '#e2e8f0', size: 18 } },
                    xaxis: { ...regPlot.layout.xaxis, gridcolor: '#334155', title: 'Actual Price' },
                    yaxis: { ...regPlot.layout.yaxis, gridcolor: '#334155', title: 'Predicted Price' },
                    autosize: true
                    }}
                    useResizeHandler={true}
                    style={{ width: "100%", height: "400px" }}
                    config={{ responsive: true, displayModeBar: false }}
                />
                ) : (
                <div style={{ padding: '40px', textAlign: 'center' }}>
                    {selectedModel ? "Plot not available for this model" : "Select a model to view plot"}
                </div>
                )}
            </div>

            {/* Regression CM */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', padding: '20px' }}>
                {confusionMatrix ? renderConfusionMatrix(confusionMatrix, `Confusion Matrix (${selectedModel})`) : <p>Loading CM...</p>}
            </div>
          </div>
        </div>
      </div>

      {/* Classification Section */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <h3 style={{ color: '#38bdf8', marginBottom: '20px' }}>Status Prediction (Classification)</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '40px', justifyContent: 'center', alignItems: 'flex-start' }}>
          
          {/* Metrics */}
          <div style={{ flex: '1', minWidth: '300px' }}>
            <h4 style={{ color: '#94a3b8', marginBottom: '10px' }}>Model Performance</h4>
            {classMetrics ? (
              <div style={{ fontSize: '1.2rem' }}>
                <p><strong>Model:</strong> Random Forest Classifier</p>
                <p><strong>Accuracy:</strong> <span style={{ color: '#4ade80' }}>{classMetrics.Accuracy}</span></p>
              </div>
            ) : <p>Loading...</p>}
          </div>

          {/* Classification CM */}
          <div style={{ flex: '1', minWidth: '300px', display: 'flex', justifyContent: 'center' }}>
            {renderConfusionMatrix(classCM, "Confusion Matrix (Status)")}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MLDashboard;
