"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, RefreshCw, Layers } from "lucide-react";
import CivicMap, { MapMarkerItem } from "@/components/CivicMap";

export default function MapPage() {
  const [markers, setMarkers] = useState<MapMarkerItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchMarkers = async () => {
    setLoading(true);
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
    try {
      const res = await fetch(`${API_BASE}/location/markers`);
      if (res.ok) {
        const data = await res.json();
        setMarkers(data);
      }
    } catch {
      // Mock markers if backend unreachable
      setMarkers([
        { id: "NMA-10001", category: "ROAD_DAMAGE", priority: "HIGH", status: "IN_PROGRESS", latitude: 13.1345, longitude: 77.5682, location_text: "BMSIT Main Gate" },
        { id: "NMA-10002", category: "GARBAGE", priority: "MEDIUM", status: "REPORTED", latitude: 12.9784, longitude: 77.6408, location_text: "Indiranagar 100ft Rd" },
        { id: "NMA-10003", category: "DRAINAGE", priority: "CRITICAL", status: "ASSIGNED", latitude: 12.9352, longitude: 77.6245, location_text: "Koramangala 5th Block" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarkers();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col">
      <header className="bg-slate-950 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="inline-flex items-center text-sm font-semibold text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <div className="flex items-center space-x-3">
            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-300">
              Active Markers: {markers.length}
            </span>
            <button
              onClick={fetchMarkers}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
              title="Refresh Map"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8 flex flex-col">
        <div className="mb-4">
          <h2 className="text-2xl font-bold">Civic Grievance Geospatial Map</h2>
          <p className="text-xs text-slate-400">
            Real-time urban defect coordinates across Bengaluru metropolitan area. Click on any pin to inspect the case.
          </p>
        </div>

        <div className="flex-1">
          <CivicMap markers={markers} />
        </div>
      </main>
    </div>
  );
}
