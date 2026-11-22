"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Send, CheckCircle2, Upload, MapPin, AlertTriangle, ShieldCheck } from "lucide-react";

export default function ReportPage() {
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    description: "",
    location_text: "",
    category: "",
    latitude: 13.1345,
    longitude: 77.5682,
  });

  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleLocationDetect = () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setFormData((prev) => ({
            ...prev,
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            location_text: prev.location_text || `GPS Coordinates: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`,
          }));
        },
        () => {
          // Default to Bangalore coordinates if location permission denied
          setFormData((prev) => ({
            ...prev,
            latitude: 12.9716,
            longitude: 77.5946,
            location_text: prev.location_text || "Bengaluru City Center",
          }));
        }
      );
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

    try {
      // 1. Submit complaint
      const res = await fetch(`${API_BASE}/complaints`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          citizen_name: formData.name,
          citizen_phone: formData.phone,
          description: formData.description,
          location_text: formData.location_text,
          latitude: formData.latitude,
          longitude: formData.longitude,
          category: formData.category || null,
          channel: "WEB",
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.message || "Failed to submit complaint");
      }

      const complaint = await res.json();

      // 2. If photo attached, upload evidence
      if (file && complaint.id) {
        const uploadData = new FormData();
        uploadData.append("file", file);
        uploadData.append("evidence_type", "CITIZEN_INITIAL");

        await fetch(`${API_BASE}/complaints/${complaint.id}/evidence`, {
          method: "POST",
          body: uploadData,
        });
      }

      setResult(complaint);
    } catch (err: any) {
      setError(err.message || "Network error. Please verify the backend is running.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="inline-flex items-center text-sm font-semibold text-slate-600 hover:text-slate-900 transition">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <div className="text-sm font-bold text-slate-800">Citizen Grievance Intake</div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-8">
        {result ? (
          <div className="bg-white rounded-2xl p-8 border border-emerald-200 shadow-sm text-center">
            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 mx-auto mb-4">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Complaint Registered Successfully!</h2>
            <div className="my-4 inline-block px-4 py-2 bg-emerald-50 rounded-lg border border-emerald-200">
              <span className="text-xs text-slate-500 uppercase tracking-wider block">Complaint Reference ID</span>
              <span className="text-2xl font-mono font-bold text-emerald-700">{result.id}</span>
            </div>

            <div className="bg-slate-50 rounded-xl p-4 text-left max-w-lg mx-auto text-sm space-y-2 border border-slate-200 my-6">
              <div className="flex justify-between">
                <span className="text-slate-500">Status:</span>
                <span className="font-semibold text-slate-800">{result.status}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Category (AI Detected):</span>
                <span className="font-semibold text-slate-800">{result.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Assigned Department:</span>
                <span className="font-semibold text-slate-800">{result.department_id || "Routing..."}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Priority Score:</span>
                <span className="font-semibold text-amber-600">{result.priority} ({result.priority_score}/100)</span>
              </div>
              {result.cluster_id && (
                <div className="flex justify-between">
                  <span className="text-slate-500">Linked Incident Cluster:</span>
                  <span className="font-semibold text-blue-600">{result.cluster_id}</span>
                </div>
              )}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-left max-w-lg mx-auto mb-6 text-sm text-blue-800">
              <div className="flex items-start space-x-2">
                <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">WhatsApp Evidence & Verification Channel Active</p>
                  <p className="text-xs text-blue-700 mt-1">
                    An evidence request prompt has been registered for your phone ({formData.phone}). You can send additional photos directly via WhatsApp to automatically attach them to #{result.id}.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-center space-x-4">
              <Link
                href={`/track?id=${result.id}`}
                className="px-6 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition"
              >
                Track Status Live
              </Link>
              <button
                onClick={() => {
                  setResult(null);
                  setFormData({ name: "", phone: "", description: "", location_text: "", category: "", latitude: 13.1345, longitude: 77.5682 });
                  setFile(null);
                }}
                className="px-6 py-2.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm transition"
              >
                Report Another Issue
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Report a Civic Problem</h2>
            <p className="text-sm text-slate-500 mb-6">
              Provide the details below. Our AI engine automatically classifies the issue, pinpoints severity, and dispatches the complaint to the right municipal authority.
            </p>

            {error && (
              <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                    Your Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g. Ramesh Kumar"
                    className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                    Phone Number (WhatsApp Active) *
                  </label>
                  <input
                    type="tel"
                    required
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="e.g. +919876543210"
                    className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                  Describe the Problem *
                </label>
                <textarea
                  required
                  rows={4}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="e.g. Deep pothole right outside college gate causing bikes to skid in rain. Water has filled up the hole."
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                />
                <span className="text-xs text-slate-400 mt-1 block">
                  Write naturally in English, Hindi, or Kannada. AI will extract category and severity.
                </span>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Location & Landmark *
                  </label>
                  <button
                    type="button"
                    onClick={handleLocationDetect}
                    className="inline-flex items-center text-xs font-semibold text-emerald-600 hover:text-emerald-700"
                  >
                    <MapPin className="w-3.5 h-3.5 mr-1" />
                    Detect Current GPS
                  </button>
                </div>
                <input
                  type="text"
                  required
                  value={formData.location_text}
                  onChange={(e) => setFormData({ ...formData, location_text: e.target.value })}
                  placeholder="e.g. Near BMSIT Main Gate, Doddaballapur Main Road, Yelahanka"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                  Attach Photo Evidence (Recommended)
                </label>
                <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-emerald-500 transition cursor-pointer relative">
                  <input
                    type="file"
                    accept="image/*,video/*"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="flex flex-col items-center">
                    <Upload className="w-8 h-8 text-slate-400 mb-2" />
                    {file ? (
                      <p className="text-sm font-semibold text-emerald-600">{file.name}</p>
                    ) : (
                      <>
                        <p className="text-sm font-medium text-slate-700">Click or drag photo/video here</p>
                        <p className="text-xs text-slate-400 mt-1">JPEG, PNG, MP4 up to 10MB</p>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-400 text-white font-bold text-sm shadow-md shadow-emerald-600/20 transition flex items-center justify-center space-x-2"
              >
                {submitting ? (
                  <span>AI Engine Analyzing & Registering...</span>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Submit Grievance</span>
                  </>
                )}
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
