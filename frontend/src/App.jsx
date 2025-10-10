import React from "react";
import Dashboard from "./pages/Dashboard";
import Navbar from "./components/Navbar";

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <Dashboard />
    </div>
  );
}

export default App;
