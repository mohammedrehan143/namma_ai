"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  ShieldAlert,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Upload,
  MapPin,
  User,
  Phone,
  Building,
  RotateCcw,
  Sparkles,
  Send,
  FileCheck
} from "lucide-react";

export default function ComplaintDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [complaint, setComplaint] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Officer Action Form States
  const [officerNotes, setOfficerNotes] = useState("");
  const [afterFile, setAfterFile] = useState<File | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [resolutionResult, setResolutionResult] = useState<any | null>(null);

  const fetchDetail = async () => {
    setLoading(true);
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "https://namma-ai.onrender.com/api";
    try {
      const res = await fetch(`${API_BASE}/complaints/${id}`);
      if (!res.ok) throw new Error("Grievance case not found");
      const data = await res.json();
      setComplaint(data);
    } catch (e: any) {
      setError(e.message || "Failed to load complaint details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) fetchDetail();
  }, [id]);

  // Handle Officer Status Progression (e.g. Accept -> IN_PROGRESS)
  const handleUpdateStatus = async (newStatus: string) => {
    setActionLoading(true);
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "https://namma-ai.onrender.com/api";
    try {
      const res = await fetch(`${API_BASE}/complaints/${id}/assign`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          notes: `Status changed to ${newStatus}`,
          status: newStatus
        }),
      });
      if (res.ok) {
        await fetchDetail();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Officer Resolution Submission with After Photo
  const handleResolveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "https://namma-ai.onrender.com/api";
    try {
      const formData = new FormData();
      formData.append("officer_notes", officerNotes);
      if (afterFile) {
        formData.append("after_media_file", afterFile);
      }

      const res = await fetch(`${API_BASE}/complaints/${id}/resolve`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || "Failed to submit resolution");
      }

      const data = await res.json();
      setResolutionResult(data);
      await fetchDetail();
    } catch (e: any) {
      alert(e.message || "Error submitting resolution");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center text-slate-500 text-sm">
        Loading case data for #{id}...
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="min-h-screen bg-slate-100 p-8 flex flex-col items-center justify-center">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm text-center max-w-md">
          <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto mb-2" />
          <h2 className="text-lg font-bold text-slate-900">Case Not Found</h2>
          <p className="text-xs text-slate-500 mt-1 mb-4">{error || "The requested grievance does not exist."}</p>
          <Link href="/dashboard" className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      {/* Top Bar */}
      <header className="bg-slate-900 text-white border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/dashboard" className="inline-flex items-center text-xs font-semibold text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-4 h-4 mr-1.5" />
            Back to Dashboard
          </Link>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400">Case Ref:</span>
            <span className="font-mono font-bold text-emerald-400 text-sm">{complaint.id}</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Complaint Details & AI Breakdown (2 cols wide) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Main Case Summary */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
              <div>
                <span className="text-xs font-mono font-bold text-slate-500 uppercase tracking-widest block">
                  {complaint.category} • {complaint.department_name || complaint.department_id}
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-1">
                  {complaint.ai_summary || complaint.raw_description}
                </h2>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider bg-slate-100 text-slate-800">
                  {complaint.status}
                </span>
                <span className="text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider bg-amber-100 text-amber-800">
                  {complaint.priority} ({complaint.priority_score}/100)
                </span>
              </div>
            </div>

            {/* Citizen Raw Report */}
            <div className="text-xs space-y-2">
              <span className="font-bold text-slate-700 uppercase tracking-wider">Citizen Statement:</span>
              <p className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 italic">
                "{complaint.raw_description}"
              </p>
            </div>

            {/* Citizen Meta & Location */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-100 text-xs">
              <div className="space-y-1">
                <span className="text-slate-400 font-semibold block uppercase">Reported By</span>
                <div className="font-bold text-slate-800 flex items-center space-x-1.5">
                  <User className="w-3.5 h-3.5 text-slate-400" />
                  <span>{complaint.citizen_name || "Anonymous Citizen"}</span>
                </div>
                <div className="text-slate-600 flex items-center space-x-1.5">
                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                  <span>{complaint.citizen_phone}</span>
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-slate-400 font-semibold block uppercase">Geographic Location</span>
                <div className="font-bold text-slate-800 flex items-center space-x-1.5">
                  <MapPin className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span className="truncate">{complaint.location_text || "Coordinates available"}</span>
                </div>
                <div className="text-slate-500 font-mono text-[11px]">
                  Lat: {complaint.latitude?.toFixed(4)}, Lon: {complaint.longitude?.toFixed(4)}
                </div>
              </div>
            </div>

            {/* Incident Cluster banner if clustered */}
            {complaint.cluster_id && (
              <div className="mt-4 p-3 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-between text-xs text-blue-900">
                <div className="flex items-center space-x-2">
                  <span className="font-bold">Part of Multi-Citizen Incident Cluster:</span>
                  <span className="font-mono font-bold bg-blue-200 px-2 py-0.5 rounded">{complaint.cluster_id}</span>
                </div>
                <span className="text-[11px] text-blue-700">Duplicate detection auto-linked this case</span>
              </div>
            )}
          </div>

          {/* Evidence Gallery & Vision AI */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <span>Citizen Evidence & Multimodal Vision Analysis ({complaint.evidence?.length || 0})</span>
            </h3>

            {complaint.evidence && complaint.evidence.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {complaint.evidence.map((ev: any) => (
                  <div key={ev.id} className="border border-slate-200 rounded-xl overflow-hidden p-3 bg-slate-50">
                    <img
                      src={`${process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api', '') || "https://namma-ai.onrender.com"}${ev.media_url}`}
                      alt="Complaint evidence"
                      className="w-full h-48 object-cover rounded-lg bg-slate-200 mb-2"
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
                        <span className="text-slate-500">AI Verified:</span>
                        <span className="font-bold text-emerald-600">
                          {ev.ai_confidence ? `${Math.round(ev.ai_confidence * 100)}% Confidence` : "Verified"}
                        </span>
                      </div>
                      {ev.ai_analysis?.visual_description && (
                        <p className="text-[11px] text-slate-600 bg-white p-2 rounded border border-slate-200 mt-1">
                          {ev.ai_analysis.visual_description}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                No initial evidence attached. WhatsApp evidence prompt was dispatched to {complaint.citizen_phone}.
              </div>
            )}
          </div>

          {/* Audit Timeline */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <Clock className="w-4 h-4 text-slate-500" />
              <span>Full Audit Timeline & Event Trail</span>
            </h3>

            <div className="space-y-4">
              {complaint.events?.map((ev: any, idx: number) => (
                <div key={ev.id || idx} className="flex items-start space-x-3 text-xs">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-800">{ev.event_type.replace(/_/g, " ")}</span>
                      <span className="text-slate-400 font-mono">
                        {new Date(ev.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-slate-600 mt-0.5">{ev.details}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Officer Action Command Panel (1 col wide) */}
        <div className="space-y-6">
          {/* Action Card */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Building className="w-4 h-4 text-slate-700" />
              <span>Officer Actions & Resolution</span>
            </h3>

            {/* Quick Status Buttons */}
            {complaint.status === "REPORTED" && (
              <button
                onClick={() => handleUpdateStatus("IN_PROGRESS")}
                disabled={actionLoading}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow transition"
              >
                Accept Case & Begin Repair
              </button>
            )}

            {/* Resolution Form */}
            <form onSubmit={handleResolveSubmit} className="space-y-4 pt-2 border-t border-slate-100">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Officer Repair Notes *
                </label>
                <textarea
                  required
                  rows={3}
                  value={officerNotes}
                  onChange={(e) => setOfficerNotes(e.target.value)}
                  placeholder="Detail the repair actions completed by the municipal crew..."
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Upload "After" Repair Proof (Photo) *
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setAfterFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-500 file:mr-2 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
                />
                <span className="text-[11px] text-slate-400 mt-1 block">
                  Vision AI will compare this photo against the original citizen evidence.
                </span>
              </div>

              <button
                type="submit"
                disabled={actionLoading}
                className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-300 text-white font-bold text-xs shadow-md shadow-emerald-600/20 transition flex items-center justify-center space-x-2"
              >
                <FileCheck className="w-4 h-4" />
                <span>{actionLoading ? "Verifying with AI..." : "Submit Verified Resolution"}</span>
              </button>
            </form>

            {/* Verification Result Feedback */}
            {resolutionResult && (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 space-y-1">
                <div className="font-bold flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Resolution AI Verification Passed!</span>
                </div>
                <p>
                  Confidence: <span className="font-bold">{Math.round(resolutionResult.ai_verification?.confidence * 100)}%</span>
                </p>
                <p className="text-[11px] text-slate-600">{resolutionResult.ai_verification?.notes}</p>
                <div className="mt-2 pt-2 border-t border-emerald-200 text-emerald-800 font-semibold">
                  Citizen confirmation prompt sent to WhatsApp.
                </div>
              </div>
            )}
          </div>

          {/* SLA Card */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm text-xs space-y-2">
            <span className="text-slate-400 uppercase font-bold block tracking-wider">SLA Target</span>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Deadline:</span>
              <span className="font-mono font-bold text-slate-800">
                {complaint.sla_deadline ? new Date(complaint.sla_deadline).toLocaleString() : "Pending"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-600">Breach Status:</span>
              <span className={complaint.is_sla_breached ? "font-bold text-rose-600" : "font-bold text-emerald-600"}>
                {complaint.is_sla_breached ? "BREACHED" : "ON SCHEDULE"}
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
