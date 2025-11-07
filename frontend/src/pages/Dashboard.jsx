import React from "react";
import ChartCard from "../components/ChartCard";

export default function Dashboard() {
  const API_BASE_URL = "http://127.0.0.1:8000";

  // All plots from backend/app.py
  const charts = [
    {
      id: "sales_over_time",
      title: "Total Sales Over Time",
      endpoint: "/sales_over_time",
      type: "plotly_html"
    },
    {
      id: "payment_mode_status",
      title: "Payment Modes vs Status",
      endpoint: "/payment_mode_status",
      type: "png"
    },
    {
      id: "customer_age_dist",
      title: "Customer Age Distribution",
      endpoint: "/customer_age_dist",
      type: "png"
    },
    {
      id: "purchase_cost_dist",
      title: "Purchase Cost Distribution",
      endpoint: "/purchase_cost_dist",
      type: "png"
    },
    {
      id: "supplier_qty",
      title: "Quantity Purchased per Supplier",
      endpoint: "/supplier_qty",
      type: "plotly_html"
    },
    {
      id: "stock_box",
      title: "Available Stock Units per Shop",
      endpoint: "/stock_box",
      type: "plotly_html"
    },
    {
      id: "sales_corr_heatmap",
      title: "Sales Correlation Heatmap",
      endpoint: "/sales_corr_heatmap",
      type: "png"
    },
    {
      id: "top_doctors",
      title: "Top 10 Doctors by Prescriptions",
      endpoint: "/top_doctors",
      type: "plotly_html"
    },
    {
      id: "prescription_trend",
      title: "Prescriptions Over Years",
      endpoint: "/prescription_trend",
      type: "png"
    },
    {
      id: "discount_vs_price",
      title: "Discount vs Final Price",
      endpoint: "/discount_vs_price",
      type: "plotly_html"
    },
    {
      id: "top_meds",
      title: "Top 10 Medicines by Revenue",
      endpoint: "/top_meds",
      type: "plotly_html"
    },
    {
      id: "shop_ratings_box",
      title: "Shop Ratings by Location",
      endpoint: "/shop_ratings_box",
      type: "plotly_html"
    },
    {
      id: "shop_ratings_hist",
      title: "Shop Ratings Distribution",
      endpoint: "/shop_ratings_hist",
      type: "png"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-6 py-6 max-w-[1920px]">
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Pharmacy EDA Dashboard</h1>
          <p className="text-gray-600">Comprehensive analytics and visualizations</p>
        </div>
        <div className="grid grid-cols-2 gap-6">
          {charts.map((chart) => (
            <ChartCard
              key={chart.id}
              title={chart.title}
              endpoint={`${API_BASE_URL}${chart.endpoint}`}
              type={chart.type}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
