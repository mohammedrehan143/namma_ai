"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Search, Clock, ShieldCheck, CheckCircle2, AlertCircle, FileText, MapPin, Building, RefreshCw } from "lucide-react";

function TrackContent() {
  const searchParams = useSearchParams();
  const initialId = searchParams.get("id") || "";

  const [complaintId, setComplaintId] = useState(initialId);
  const [complaint, setComplaint] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComplaint = async (id: string) => {
    if (!id.trim()) return;
    setLoading(true);
    setError(null);

    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
    try {
      const res = await fetch(`${API_BASE}/complaints/${id.trim()}`);
      if (!res.ok) {
        throw new Error("Complaint ID not found. Please double check the ID format (e.g. NMA-10001).");
      }
      const data = await res.json();
      setComplaint(data);
    } catch (err: any) {
      setError(err.message || "Failed to load complaint");
      setComplaint(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialId) {
      fetchComplaint(initialId);
    }
  }, [initialId]);

  return (
    <div className="max-w-4xl mx-auto w-full px-4 py-8">
      {/* Search Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm mb-6">
        <h2 className="text-xl font-bold text-slate-900 mb-2">Track Grievance Resolution</h2>
        <p className="text-xs text-slate-500 mb-4">
          Enter your reference ID below to inspect AI classification, officer assignment, and live verification status.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetchComplaint(complaintId);
          }}
          className="flex gap-2"
        >
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={complaintId}
              onChange={(e) => setComplaintId(e.target.value)}
              placeholder="e.g. NMA-10001"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm font-mono font-medium"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm transition"
          >
            {loading ? "Searching..." : "Track"}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Complaint Detail Card */}
      {complaint && (
        <div className="space-y-6">
          {/* Main Info */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4 mb-4">
              <div>
                <span className="text-xs font-mono font-bold text-emerald-700 px-2.5 py-1 bg-emerald-50 border border-emerald-200 rounded-md">
                  {complaint.id}
                </span>
                <h3 className="text-lg font-bold text-slate-900 mt-2">{complaint.ai_summary || complaint.raw_description}</h3>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider bg-slate-100 text-slate-800">
                  {complaint.status}
                </span>
                <span className="text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider bg-amber-100 text-amber-800">
                  {complaint.priority} Priority
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-slate-400 block mb-1 font-semibold uppercase">Category</span>
                <span className="font-bold text-slate-800">{complaint.category}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-slate-400 block mb-1 font-semibold uppercase">Department</span>
                <span className="font-bold text-slate-800">{complaint.department_name || complaint.department_id}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-slate-400 block mb-1 font-semibold uppercase">Location</span>
                <span className="font-bold text-slate-800 truncate block">{complaint.location_text || "Geo-tagged"}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-slate-400 block mb-1 font-semibold uppercase">SLA Target</span>
                <span className="font-bold text-emerald-600 block">
                  {complaint.sla_deadline ? new Date(complaint.sla_deadline).toLocaleDateString() : "Pending"}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-600">
              <p className="font-medium text-slate-800 mb-1">Citizen Statement:</p>
              <p className="bg-slate-50 p-3 rounded-lg border border-slate-200 italic">
                "{complaint.raw_description}"
              </p>
            </div>
          </div>

          {/* Evidence Grid */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h4 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Attached Evidence & Vision AI Analysis ({complaint.evidence?.length || 0})</span>
            </h4>

            {complaint.evidence && complaint.evidence.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {complaint.evidence.map((ev: any) => (
                  <div key={ev.id} className="border border-slate-200 rounded-xl overflow-hidden p-3 bg-slate-50">
                    <img
                      src={`${process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api', '') || "http://localhost:8000"}${ev.media_url}`}
                      alt="Complaint evidence"
                      className="w-full h-44 object-cover rounded-lg bg-slate-200 mb-2"
                      onError={(e) => {
                        (e.target as any).src = "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop&q=60";
                      }}
                    />
                    <div className="text-xs space-y-1">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Source:</span>
                        <span className="font-semibold text-slate-700">{ev.evidence_type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">AI Confidence:</span>
                        <span className="font-semibold text-emerald-600">
                          {ev.ai_confidence ? `${Math.round(ev.ai_confidence * 100)}%` : "Verified"}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                No photographic evidence uploaded yet. You can attach photos by sending them on WhatsApp.
              </div>
            )}
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h4 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <Clock className="w-4 h-4 text-slate-500" />
              <span>Grievance Audit Trail</span>
            </h4>

            <div className="space-y-4">
              {complaint.events?.map((ev: any, idx: number) => (
                <div key={ev.id || idx} className="flex items-start space-x-3 text-xs">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-800">{ev.event_type.replace(/_/g, " ")}</span>
                      <span className="text-slate-400 font-mono">
                        {new Date(ev.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                    <p className="text-slate-500 mt-0.5">{ev.details || "Status updated"}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function TrackPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="inline-flex items-center text-sm font-semibold text-slate-600 hover:text-slate-900 transition">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <div className="text-sm font-bold text-slate-800">Public Grievance Tracker</div>
        </div>
      </header>

      <Suspense fallback={<div className="p-8 text-center text-slate-400">Loading tracker...</div>}>
        <TrackContent />
      </Suspense>
    </div>
  );
}
