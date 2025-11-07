import React from "react";

export default function Navbar() {
  return (
    <nav className="bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-center">
          <span className="text-2xl mr-3">💊</span>
          <h1 className="text-2xl font-bold">Pharmacy Data Dashboard</h1>
        </div>
      </div>
    </nav>
  );
}
