import React, { useState } from 'react';
import PlotlyGraph from './components/PlotlyGraph';
import MLDashboard from './components/MLDashboard';
import EDADashboard from './components/EDADashboard';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const charts = [
    { endpoint: '/sales_over_time', title: 'Total Sales Over Time' },
    { endpoint: '/payment_mode_status', title: 'Payment Modes vs Status' },
    { endpoint: '/customer_age_dist', title: 'Customer Age Distribution' },
    { endpoint: '/purchase_cost_dist', title: 'Purchase Cost Distribution' },
    { endpoint: '/supplier_qty', title: 'Quantity Purchased per Supplier' },
    { endpoint: '/stock_box', title: 'Available Stock Units per Shop' },
    { endpoint: '/sales_corr_heatmap', title: 'Sales Correlation Heatmap' },
    { endpoint: '/top_doctors', title: 'Top 10 Doctors by Prescriptions' },
    { endpoint: '/prescription_trend', title: 'Prescriptions Over Years' },
    { endpoint: '/discount_vs_price', title: 'Discount vs Final Price' },
    { endpoint: '/top_meds', title: 'Top 10 Medicines by Revenue' },
    { endpoint: '/shop_ratings_box', title: 'Shop Ratings by Location' },
    { endpoint: '/shop_ratings_hist', title: 'Shop Ratings Distribution' },
  ];

  return (
    <div className="App">
      <header className="header">
        <h1>Pharmacy Analytics Dashboard</h1>
        <p>Real-time Interactive Insights & ML Predictions</p>
      </header>
      
      <nav className="tab-nav">
        <button 
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`} 
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`tab-btn ${activeTab === 'ml' ? 'active' : ''}`} 
          onClick={() => setActiveTab('ml')}
        >
          ML Models
        </button>
        <button 
          className={`tab-btn ${activeTab === 'eda' ? 'active' : ''}`} 
          onClick={() => setActiveTab('eda')}
        >
          EDA Analysis
        </button>
      </nav>

      {activeTab === 'dashboard' && (
        <main className="dashboard-grid">
          {charts.map((chart, index) => (
            <PlotlyGraph 
              key={index} 
              endpoint={chart.endpoint} 
              title={chart.title} 
            />
          ))}
        </main>
      )}

      {activeTab === 'ml' && (
        <section style={{ padding: '0 24px 48px', maxWidth: '1600px', margin: '0 auto' }}>
          <MLDashboard />
        </section>
      )}

      {activeTab === 'eda' && (
        <section style={{ padding: '0 24px 48px', maxWidth: '1600px', margin: '0 auto' }}>
          <EDADashboard />
        </section>
      )}
    </div>
  );
}

export default App;
