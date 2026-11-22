"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  PhoneCall,
  MessageSquare,
  Sparkles,
  Users,
  ShieldAlert,
  FileCheck
} from "lucide-react";

export default function DemoPage() {
  const [steps, setSteps] = useState<any[]>([]);
  const [running, setRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState<number | null>(null);
  const [demoResult, setDemoResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
    fetch(`${API_BASE}/demo/steps`)
      .then((res) => res.json())
      .then((data) => setSteps(data))
      .catch(() => {});
  }, []);

  const runFullDemo = async () => {
    setRunning(true);
    setError(null);
    setCurrentStep(1);

    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
    try {
      // Simulate visual progression
      const interval = setInterval(() => {
        setCurrentStep((prev) => (prev && prev < 20 ? prev + 1 : prev));
      }, 150);

      const res = await fetch(`${API_BASE}/demo/run-full-scenario`, {
        method: "POST",
      });

      clearInterval(interval);
      setCurrentStep(20);

      if (!res.ok) {
        throw new Error("Demo execution encountered an issue.");
      }

      const data = await res.json();
      setDemoResult(data);
    } catch (e: any) {
      setError(e.message || "Failed to execute demo scenario");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col font-sans">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur border-b border-slate-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="inline-flex items-center text-xs font-semibold text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-4 h-4 mr-1.5" />
            Back to Home
          </Link>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-800 px-2.5 py-1 rounded-md">
              HACKATHON DEMO SHOWCASE
            </span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner */}
        <div className="bg-gradient-to-r from-slate-900 to-slate-900/60 p-6 sm:p-8 rounded-3xl border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center space-x-1.5 text-xs font-bold text-emerald-400">
              <Sparkles className="w-4 h-4" />
              <span>Judge & Evaluator Interactive Scenario</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              End-to-End Pothole Resolution & Reopening Lifecycle
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Experience the complete 20-step flow from citizen voice reporting, multimodal evidence auditing, duplicate incident clustering, to officer repair and closed-loop citizen verification rejection/reopening.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full md:w-auto">
            <button
              onClick={runFullDemo}
              disabled={running}
              className="px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-700 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition flex items-center justify-center space-x-2"
            >
              <Play className={`w-4 h-4 ${running ? "animate-spin" : ""}`} />
              <span>{running ? "Simulating 20-Step Pipeline..." : "Run Complete 20-Step Live Demo"}</span>
            </button>
            {demoResult && (
              <button
                onClick={() => {
                  setDemoResult(null);
                  setCurrentStep(null);
                }}
                className="px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition flex items-center justify-center space-x-1"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>

        {/* Demo Result Callout Card */}
        {demoResult && (
          <div className="bg-emerald-950/40 border border-emerald-500/40 p-6 rounded-2xl animate-in fade-in duration-300 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold text-white text-base">Scenario Executed Successfully!</h3>
              </div>
              <div className="flex items-center space-x-3">
                <Link
                  href={`/dashboard/${demoResult.demo_complaint_id}`}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition flex items-center space-x-1"
                >
                  <span>Open Case in Dashboard</span>
                  <ExternalLink className="w-3 h-3 ml-1" />
                </Link>
                <Link
                  href="/dashboard"
                  className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition"
                >
                  View Command Center
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
                <span className="text-slate-400 block mb-0.5">Primary Case Reference</span>
                <span className="font-mono font-bold text-emerald-400 text-sm">{demoResult.demo_complaint_id}</span>
              </div>
              <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
                <span className="text-slate-400 block mb-0.5">Formed Incident Cluster</span>
                <span className="font-mono font-bold text-blue-400 text-sm">{demoResult.incident_cluster_id}</span>
              </div>
              <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
                <span className="text-slate-400 block mb-0.5">Final Lifecycle State</span>
                <span className="font-bold text-rose-400 text-sm">REOPENED & ESCALATED</span>
              </div>
            </div>
          </div>
        )}

        {/* 20 Step Narrative Visualizer */}
        <div className="bg-slate-900/60 rounded-3xl border border-slate-800 p-6 sm:p-8 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <span>Full 20-Phase Verification Sequence</span>
            </h3>
            <span className="text-xs text-slate-400">
              {currentStep ? `Step ${currentStep} of 20 Active` : "Ready to execute"}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {steps.map((st) => {
              const isPast = currentStep !== null && st.step <= currentStep;
              const isCurrent = currentStep === st.step;

              return (
                <div
                  key={st.step}
                  className={`p-4 rounded-2xl border text-xs transition duration-200 flex flex-col justify-between ${
                    isCurrent
                      ? "bg-emerald-950/40 border-emerald-500 ring-2 ring-emerald-500/20 shadow-lg shadow-emerald-500/10"
                      : isPast
                      ? "bg-slate-900/90 border-emerald-900/60"
                      : "bg-slate-900/30 border-slate-800/60 opacity-60"
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-slate-400 text-[10px]">
                        STEP {st.step < 10 ? `0${st.step}` : st.step}
                      </span>
                      {isPast ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <span className="w-2 h-2 rounded-full bg-slate-700" />
                      )}
                    </div>
                    <h4 className="font-bold text-white text-xs">{st.title}</h4>
                    <p className="text-[11px] text-slate-400 leading-snug">{st.action}</p>
                  </div>

                  <div className="mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500 font-mono">
                    Actor: {st.actor}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
}
