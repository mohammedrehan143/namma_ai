"use client";

import React, { useState } from "react";
import Link from "next/link";
import { MapPin, AlertCircle, Info, ExternalLink } from "lucide-react";

export interface MapMarkerItem {
  id: string;
  category: string;
  department_id?: string;
  priority: string;
  status: string;
  latitude: number;
  longitude: number;
  location_text?: string;
  cluster_id?: string;
}

interface CivicMapProps {
  markers: MapMarkerItem[];
  selectedId?: string;
  onSelectMarker?: (marker: MapMarkerItem) => void;
}

export default function CivicMap({ markers, selectedId, onSelectMarker }: CivicMapProps) {
  const [activeMarker, setActiveMarker] = useState<MapMarkerItem | null>(null);

  // Bengaluru bounding box
  const minLat = 12.80;
  const maxLat = 13.20;
  const minLon = 77.45;
  const maxLon = 77.80;

  // Convert lat/lon to percentage position
  const getCoordinates = (lat: number, lon: number) => {
    const x = ((lon - minLon) / (maxLon - minLon)) * 100;
    const y = ((maxLat - lat) / (maxLat - minLat)) * 100;
    return {
      x: Math.max(5, Math.min(95, x)),
      y: Math.max(5, Math.min(95, y)),
    };
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toUpperCase()) {
      case "CRITICAL":
        return "bg-rose-500 ring-rose-300 text-white";
      case "HIGH":
        return "bg-amber-500 ring-amber-300 text-white";
      case "MEDIUM":
        return "bg-blue-500 ring-blue-300 text-white";
      default:
        return "bg-emerald-500 ring-emerald-300 text-white";
    }
  };

  return (
    <div className="relative w-full h-[520px] rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden shadow-inner select-none">
      {/* Grid Pattern / Radial civic map backdrop */}
      <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px]" />
      
      {/* Map Boundary Labels */}
      <div className="absolute top-3 left-4 text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest pointer-events-none">
        Bengaluru Metropolitan Civic Grid (12.80°N - 13.20°N, 77.45°E - 77.80°E)
      </div>

      <div className="absolute bottom-3 left-4 flex items-center space-x-3 text-xs text-slate-400 bg-slate-900/80 backdrop-blur px-3 py-1.5 rounded-lg border border-slate-800 pointer-events-none">
        <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-rose-500 mr-1.5 inline-block" /> Critical</span>
        <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 mr-1.5 inline-block" /> High</span>
        <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-blue-500 mr-1.5 inline-block" /> Medium</span>
        <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 mr-1.5 inline-block" /> Low</span>
      </div>

      {/* Pins */}
      {markers.map((marker) => {
        const { x, y } = getCoordinates(marker.latitude, marker.longitude);
        const isSelected = selectedId === marker.id || activeMarker?.id === marker.id;

        return (
          <div
            key={marker.id}
            style={{ left: `${x}%`, top: `${y}%` }}
            className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer z-10 group"
            onClick={() => {
              setActiveMarker(marker);
              if (onSelectMarker) onSelectMarker(marker);
            }}
          >
            {/* Pulsing indicator for Critical issues */}
            {marker.priority === "CRITICAL" && (
              <span className="absolute -inset-1 rounded-full bg-rose-500/50 animate-ping" />
            )}

            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center shadow-lg transition-transform group-hover:scale-125 ring-4 ${getPriorityColor(
                marker.priority
              )} ${isSelected ? "scale-125 ring-white" : ""}`}
            >
              <MapPin className="w-4 h-4" />
            </div>

            {/* Hover tooltip */}
            <div className="opacity-0 group-hover:opacity-100 transition pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-slate-900 text-white text-[11px] font-semibold py-1 px-2 rounded-md shadow-xl whitespace-nowrap z-20 border border-slate-700">
              {marker.id} — {marker.category}
            </div>
          </div>
        );
      })}

      {/* Selected Marker Popup Card */}
      {activeMarker && (
        <div className="absolute top-4 right-4 w-72 bg-white rounded-xl shadow-2xl border border-slate-200 p-4 z-30 animate-in fade-in duration-200">
          <div className="flex items-start justify-between">
            <span className="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              {activeMarker.id}
            </span>
            <button
              onClick={() => setActiveMarker(null)}
              className="text-slate-400 hover:text-slate-600 text-xs font-bold"
            >
              ✕
            </button>
          </div>

          <h4 className="font-bold text-slate-900 text-sm mt-2">{activeMarker.category}</h4>
          <p className="text-xs text-slate-500 mt-1 line-clamp-2">
            {activeMarker.location_text || `Coordinates: ${activeMarker.latitude.toFixed(4)}, ${activeMarker.longitude.toFixed(4)}`}
          </p>

          <div className="mt-3 flex items-center justify-between text-xs pt-2 border-t border-slate-100">
            <span className="font-semibold text-slate-700">{activeMarker.status}</span>
            <span className="font-bold text-amber-600">{activeMarker.priority}</span>
          </div>

          <div className="mt-3 pt-2">
            <Link
              href={`/dashboard/${activeMarker.id}`}
              className="w-full py-1.5 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition flex items-center justify-center space-x-1"
            >
              <span>View Case Details</span>
              <ExternalLink className="w-3 h-3" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
