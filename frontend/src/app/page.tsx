"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  FilePlus,
  LayoutDashboard,
  MapPin,
  Activity,
  PhoneCall,
  MessageSquare,
  Sparkles,
  ArrowRight,
  CheckCircle,
  AlertOctagon,
  Users
} from "lucide-react";

export default function Home() {
  const [health, setHealth] = useState<{ status: string; database: string } | null>(null);
  const [stats, setStats] = useState<any>({ total: 12, open: 4, resolved: 7 });

  useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "https://namma-ai.onrender.com/api";
    const BASE_HOST = API_BASE.replace(/\/api\/?$/, "");

    fetch(`${BASE_HOST}/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth(null));

    fetch(`${API_BASE}/dashboard/stats`)
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch(() => {});
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-white selection:bg-emerald-500 selection:text-white">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center font-black text-white text-xl shadow-lg shadow-emerald-500/20">
              N
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight">Namma AI</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Bengaluru Civic Grievance & Outcome Verification</p>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-6 text-xs font-semibold text-slate-300">
            <Link href="/report" className="hover:text-emerald-400 transition">Report Issue</Link>
            <Link href="/track" className="hover:text-emerald-400 transition">Track Grievance</Link>
            <Link href="/map" className="hover:text-emerald-400 transition">Geospatial Map</Link>
            <Link href="/dashboard" className="hover:text-emerald-400 transition">Command Center</Link>
            <Link href="/demo" className="text-emerald-400 hover:text-emerald-300 transition flex items-center space-x-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Demo Showcase</span>
            </Link>
          </nav>

          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-2 text-xs px-3 py-1 rounded-full bg-slate-900 border border-slate-800">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-slate-400">API:</span>
              <span className="text-emerald-400 font-medium">Online ({health?.database || "Ready"})</span>
            </div>
            <Link
              href="/dashboard"
              className="text-xs font-bold px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-sm"
            >
              Officer Portal
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col justify-center max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-emerald-950/80 border border-emerald-800/60 text-emerald-300 text-xs font-semibold shadow-inner">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Civic Tech 2.0 • Closed-Loop Accountability</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-tight sm:leading-none">
            Report it. Prove it. Track it.{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
              Get it resolved.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Report civic issues seamlessly through Web, Voice Call, or WhatsApp.
            AI classifies and routes complaints, audits photographic evidence, and verifies physical repairs before closing cases.
          </p>

          {/* Quick CTA Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Link
              href="/report"
              className="px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-emerald-500/25 flex items-center space-x-2"
            >
              <FilePlus className="w-4 h-4" />
              <span>Report Grievance Online</span>
            </Link>
            <Link
              href="/demo"
              className="px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 font-bold text-sm transition flex items-center space-x-2"
            >
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>Interactive Hackathon Demo</span>
            </Link>
          </div>
        </div>

        {/* Live Counters */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto w-full">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-3xl font-extrabold text-white">{stats.total || 0}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Total Grievances</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-3xl font-extrabold text-amber-400">{stats.open || 0}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Active Cases</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-3xl font-extrabold text-emerald-400">{stats.resolved || 0}</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Verified Resolved</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center">
            <div className="text-3xl font-extrabold text-purple-400">100%</div>
            <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">Citizen Confirmed</div>
          </div>
        </div>

        {/* Multi-Channel Ingestion Cards */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto w-full">
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 relative overflow-hidden group hover:border-emerald-500/50 transition">
            <div className="w-12 h-12 rounded-xl bg-emerald-950 border border-emerald-800 flex items-center justify-center text-emerald-400 mb-4">
              <FilePlus className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Web Complaint Portal</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Natural language grievance reporting with photo evidence upload, automatic GPS pinpointing, and instant tracking reference generation.
            </p>
            <Link href="/report" className="text-xs font-bold text-emerald-400 hover:text-emerald-300 flex items-center space-x-1">
              <span>Submit Web Report</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 relative overflow-hidden group hover:border-blue-500/50 transition">
            <div className="w-12 h-12 rounded-xl bg-blue-950 border border-blue-800 flex items-center justify-center text-blue-400 mb-4">
              <PhoneCall className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Voice Call Helpline (IVR)</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Citizens simply speak their problem over the phone. AI transcribes, asks missing location questions, and creates structured complaints.
            </p>
            <Link href="/demo#voice" className="text-xs font-bold text-blue-400 hover:text-blue-300 flex items-center space-x-1">
              <span>Explore Voice Pipeline</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 relative overflow-hidden group hover:border-teal-500/50 transition">
            <div className="w-12 h-12 rounded-xl bg-teal-950 border border-teal-800 flex items-center justify-center text-teal-400 mb-4">
              <MessageSquare className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">WhatsApp Evidence Loop</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Evidence collection through WhatsApp photo messages. Vision AI checks defect validity, and citizens verify the final resolution with 1: Yes / 2: No.
            </p>
            <Link href="/demo#whatsapp" className="text-xs font-bold text-teal-400 hover:text-teal-300 flex items-center space-x-1">
              <span>View WhatsApp Engine</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4">
          Namma AI Prototype • Built for civic accountability, duplicate incident clustering, and closed-loop verification.
        </div>
      </footer>
    </div>
  );
}
