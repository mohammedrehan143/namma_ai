"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  AlertTriangle,
  Clock,
  CheckCircle2,
  RotateCcw,
  Layers,
  Search,
  Filter,
  RefreshCw,
  ExternalLink,
  MapPin,
  Users,
  Activity
} from "lucide-react";
import CivicMap, { MapMarkerItem } from "@/components/CivicMap";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>({
    total: 0,
    open: 0,
    in_progress: 0,
    resolved: 0,
    reopened: 0,
    critical: 0,
    high: 0,
    sla_breached: 0,
  });

  const [complaints, setComplaints] = useState<any[]>([]);
  const [clusters, setClusters] = useState<any[]>([]);
  const [markers, setMarkers] = useState<MapMarkerItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("");
  const [activeTab, setActiveTab] = useState<"table" | "map" | "clusters">("table");

  const loadData = async () => {
    setLoading(true);
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
    try {
      // 1. Load Stats
      const statsRes = await fetch(`${API_BASE}/dashboard/stats`);
      if (statsRes.ok) setStats(await statsRes.json());

      // 2. Load Complaints
      let url = `${API_BASE}/complaints?limit=100`;
      if (statusFilter) url += `&status=${statusFilter}`;
      if (priorityFilter) url += `&priority=${priorityFilter}`;
      if (departmentFilter) url += `&department_id=${departmentFilter}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;

      const compRes = await fetch(url);
      if (compRes.ok) {
        const compData = await compRes.json();
        setComplaints(compData.items || []);
      }

      // 3. Load Clusters
      const clusterRes = await fetch(`${API_BASE}/clusters`);
      if (clusterRes.ok) setClusters(await clusterRes.json());

      // 4. Load Map Markers
      const markerRes = await fetch(`${API_BASE}/location/markers`);
      if (markerRes.ok) setMarkers(await markerRes.json());
    } catch (e) {
      console.error("Dashboard fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, priorityFilter, departmentFilter, search]);

  const getPriorityBadge = (prio: string) => {
    switch (prio) {
      case "CRITICAL":
        return "bg-rose-100 text-rose-800 border-rose-200";
      case "HIGH":
        return "bg-amber-100 text-amber-800 border-amber-200";
      case "MEDIUM":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "RESOLVED":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "REOPENED":
      case "ESCALATED":
        return "bg-rose-50 text-rose-700 border-rose-200 animate-pulse";
      case "IN_PROGRESS":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "CITIZEN_VERIFICATION":
        return "bg-purple-50 text-purple-700 border-purple-200";
      default:
        return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      {/* Officer Header */}
      <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Link href="/" className="w-9 h-9 rounded-lg bg-emerald-500 flex items-center justify-center font-bold text-white text-lg">
              N
            </Link>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-bold">Civic Officer Command Dashboard</h1>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
                  LIVE CAD
                </span>
              </div>
              <p className="text-xs text-slate-400">Bengaluru Municipal Grievance & Outcome Operations</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={loadData}
              className="inline-flex items-center text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <Link
              href="/report"
              className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition"
            >
              + New Complaint
            </Link>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* KPI Cards Row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-xs font-medium uppercase tracking-wider">Total</span>
              <Layers className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-2xl font-bold text-slate-900">{stats.total}</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-xs font-medium uppercase tracking-wider">Open Queue</span>
              <Clock className="w-4 h-4 text-amber-500" />
            </div>
            <div className="text-2xl font-bold text-amber-600">{stats.open}</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-xs font-medium uppercase tracking-wider">Critical</span>
              <ShieldAlert className="w-4 h-4 text-rose-500" />
            </div>
            <div className="text-2xl font-bold text-rose-600">{stats.critical}</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-xs font-medium uppercase tracking-wider">SLA Overdue</span>
              <AlertTriangle className="w-4 h-4 text-orange-500" />
            </div>
            <div className="text-2xl font-bold text-orange-600">{stats.sla_breached}</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-xs font-medium uppercase tracking-wider">Resolved</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="text-2xl font-bold text-emerald-600">{stats.resolved}</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between text-slate-500 mb-1">
              <span className="text-xs font-medium uppercase tracking-wider">Reopened</span>
              <RotateCcw className="w-4 h-4 text-purple-500" />
            </div>
            <div className="text-2xl font-bold text-purple-600">{stats.reopened}</div>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center justify-between border-b border-slate-200 pb-2">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab("table")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition ${
                activeTab === "table" ? "bg-slate-900 text-white shadow-sm" : "bg-white text-slate-600 hover:bg-slate-200"
              }`}
            >
              Cases List ({complaints.length})
            </button>
            <button
              onClick={() => setActiveTab("map")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                activeTab === "map" ? "bg-slate-900 text-white shadow-sm" : "bg-white text-slate-600 hover:bg-slate-200"
              }`}
            >
              <MapPin className="w-3.5 h-3.5" />
              <span>Geospatial Map</span>
            </button>
            <button
              onClick={() => setActiveTab("clusters")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
                activeTab === "clusters" ? "bg-slate-900 text-white shadow-sm" : "bg-white text-slate-600 hover:bg-slate-200"
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Incident Clusters ({clusters.length})</span>
            </button>
          </div>
        </div>

        {/* Filters Bar */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap gap-3 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by ID, keyword, address..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadData()}
              className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs text-slate-700 bg-white focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="REPORTED">REPORTED</option>
            <option value="ASSIGNED">ASSIGNED</option>
            <option value="IN_PROGRESS">IN_PROGRESS</option>
            <option value="RESOLUTION_SUBMITTED">RESOLUTION_SUBMITTED</option>
            <option value="CITIZEN_VERIFICATION">CITIZEN_VERIFICATION</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="REOPENED">REOPENED</option>
            <option value="ESCALATED">ESCALATED</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs text-slate-700 bg-white focus:outline-none"
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs text-slate-700 bg-white focus:outline-none"
          >
            <option value="">All Departments</option>
            <option value="ROADS">Roads & Maintenance</option>
            <option value="SANITATION">Solid Waste</option>
            <option value="DRAINAGE">Stormwater Drainage</option>
            <option value="WATER">Water Supply</option>
            <option value="ELECTRICAL">Street Lighting</option>
            <option value="PUBLIC_WORKS">Public Works</option>
          </select>
        </div>

        {/* TAB 1: CASES TABLE */}
        {activeTab === "table" && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Case ID</th>
                    <th className="py-3 px-4">Category & Summary</th>
                    <th className="py-3 px-4">Department</th>
                    <th className="py-3 px-4">Priority</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Incident Cluster</th>
                    <th className="py-3 px-4">SLA Deadline</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {complaints.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-slate-400">
                        No civic complaints found matching the criteria.
                      </td>
                    </tr>
                  ) : (
                    complaints.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-50 transition">
                        <td className="py-3 px-4 font-mono font-bold text-slate-900">
                          <Link href={`/dashboard/${c.id}`} className="hover:text-emerald-600 hover:underline">
                            {c.id}
                          </Link>
                        </td>
                        <td className="py-3 px-4 max-w-xs">
                          <div className="font-semibold text-slate-800 truncate">{c.ai_summary || c.raw_description}</div>
                          <div className="text-[11px] text-slate-400 truncate">{c.location_text || "Geo-tagged"}</div>
                        </td>
                        <td className="py-3 px-4 font-medium text-slate-700">{c.department_id || "Unassigned"}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getPriorityBadge(c.priority)}`}>
                            {c.priority} ({c.priority_score})
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusBadge(c.status)}`}>
                            {c.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px]">
                          {c.cluster_id ? (
                            <span className="text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                              {c.cluster_id}
                            </span>
                          ) : (
                            <span className="text-slate-400">—</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                          {c.sla_deadline ? new Date(c.sla_deadline).toLocaleDateString() : "—"}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Link
                            href={`/dashboard/${c.id}`}
                            className="inline-flex items-center text-xs font-semibold text-emerald-600 hover:text-emerald-800"
                          >
                            <span>Manage</span>
                            <ExternalLink className="w-3 h-3 ml-1" />
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 2: GEOSPATIAL MAP */}
        {activeTab === "map" && (
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <CivicMap markers={markers} />
          </div>
        )}

        {/* TAB 3: INCIDENT CLUSTERS */}
        {activeTab === "clusters" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {clusters.length === 0 ? (
              <div className="col-span-2 bg-white p-8 rounded-xl text-center text-slate-400 border border-slate-200">
                No active duplicate incident clusters formed yet.
              </div>
            ) : (
              clusters.map((cl) => (
                <div key={cl.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-blue-50 text-blue-700 border border-blue-200">
                      {cl.id}
                    </span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 flex items-center space-x-1">
                      <Users className="w-3 h-3" />
                      <span>{cl.report_count} Affected Citizens</span>
                    </span>
                  </div>

                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{cl.title}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Category: <span className="font-medium text-slate-700">{cl.category}</span>
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-100 text-xs">
                    <span className="text-slate-400 font-semibold block mb-1">Grouped Complaint IDs:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {cl.complaint_ids?.map((cid: string) => (
                        <Link
                          key={cid}
                          href={`/dashboard/${cid}`}
                          className="font-mono text-[11px] bg-slate-100 hover:bg-slate-200 px-2 py-0.5 rounded text-slate-700"
                        >
                          {cid}
                        </Link>
                      ))}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}
