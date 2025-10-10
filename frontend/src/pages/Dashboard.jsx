import React, { useEffect, useState } from "react";
import axios from "axios";
import ChartCard from "../components/ChartCard";

export default function Dashboard() {
  const [charts, setCharts] = useState([]);
  const [loading, setLoading] = useState(true);

  const endpoints = [
    "sales-over-time",
    "payment-mode-status",
    "customer-age",
    "purchase-cost",
    "supplier-quantity",
    "stock-units",
    "sales-correlation",
    "top-doctors",
    "prescriptions-trend",
    "discount-finalprice",
    "top-medicines",
    "shop-ratings"
  ];

  useEffect(() => {
    async function fetchCharts() {
      try {
        const promises = endpoints.map(ep =>
          axios.get(`http://127.0.0.1:8000/${ep}`)
        );
        const responses = await Promise.all(promises);
        const results = responses.map((r, i) => ({
          title: endpoints[i].replace(/-/g, " ").toUpperCase(),
          data: r.data
        }));
        setCharts(results);
      } catch (err) {
        console.error("Error fetching charts:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchCharts();
  }, []);

  if (loading) return <p className="text-center mt-10">Loading dashboard...</p>;

  return (
    <div className="p-6 grid md:grid-cols-2 gap-6">
      {charts.map((chart, i) => (
        <ChartCard key={i} title={chart.title} data={chart.data} />
      ))}
    </div>
  );
}
