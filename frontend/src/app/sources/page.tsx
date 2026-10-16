"use client";

import { useEffect, useState } from "react";
import {
  Database, RefreshCw, CheckCircle2, XCircle, AlertTriangle,
  ExternalLink, ShieldCheck, Clock, Layers
} from "lucide-react";
import { fetchSourceRegistry, fetchRefreshStatus, triggerRefresh, SourceEntry, RefreshStatus } from "@/lib/api";

export default function SourcesPage() {
  const [sources, setSources] = useState<SourceEntry[]>([]);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    const [srcData, refData] = await Promise.all([
      fetchSourceRegistry(),
      fetchRefreshStatus()
    ]);
    setSources(srcData);
    setRefreshStatus(refData);
  }

  async function handleManualTrigger() {
    setRefreshing(true);
    setTriggerMsg("Triggering Cinemax ingestion pipeline...");
    try {
      const res = await triggerRefresh();
      setTriggerMsg("Ingestion initiated in background. Refreshing status in a few seconds...");
      setTimeout(() => {
        loadData();
        setRefreshing(false);
      }, 3000);
    } catch (e: any) {
      setTriggerMsg(`Error: ${e.message}`);
      setRefreshing(false);
    }
  }

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-cinemax-border pb-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold">
            <Database className="w-3.5 h-3.5" />
            Transparency & Provenance Registry
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">
            Data Source Registry & System Status
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl">
            Live operational status, access methods, rate limits, zero-cost verification, and legal licensing terms for every data provider integrated into Cinemax.
          </p>
        </div>

        {/* Manual Refresh Trigger */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <button
            onClick={handleManualTrigger}
            disabled={refreshing}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold px-4 py-2.5 rounded-xl text-xs transition-colors shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
            {refreshing ? "Triggering..." : "Trigger Refresh (Manual Dispatch)"}
          </button>
        </div>
      </div>

      {triggerMsg && (
        <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs flex items-center gap-2">
          <Clock className="w-4 h-4 flex-shrink-0" />
          {triggerMsg}
        </div>
      )}

      {/* Scheduled Refresh Status Card */}
      <div className="glass-panel rounded-2xl p-6 border border-cinemax-border grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
        <div className="space-y-1">
          <span className="text-slate-400 uppercase tracking-wider text-[10px]">Midnight Automatic Refresh:</span>
          <div className="text-white font-bold text-sm flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-emerald-400" />
            12:00 AM IST (18:30 UTC Daily)
          </div>
          <p className="text-slate-500 text-[11px]">Calculated UTC schedule with idempotent database upserts.</p>
        </div>

        <div className="space-y-1">
          <span className="text-slate-400 uppercase tracking-wider text-[10px]">Last Successful Refresh (IST):</span>
          <div className="text-emerald-400 font-mono font-bold text-sm">
            {refreshStatus?.last_successful_refresh_ist || "Scheduled for 12:00 AM IST"}
          </div>
          <p className="text-slate-500 text-[11px]">UTC: {refreshStatus?.last_successful_refresh_utc || "18:30 UTC"}</p>
        </div>

        <div className="space-y-1">
          <span className="text-slate-400 uppercase tracking-wider text-[10px]">Active Ingestion Adapters:</span>
          <div className="text-white font-bold text-sm">
            {refreshStatus?.active_sources.length || 0} Providers Active
          </div>
          <div className="flex items-center gap-1.5 text-emerald-400 text-[11px] font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            100% Zero Mandatory Cost
          </div>
        </div>
      </div>

      {/* Provider Registry Table */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-blue-400" />
          Integrated Providers Status Grid
        </h3>

        <div className="grid grid-cols-1 gap-6">
          {sources.map((src) => (
            <div key={src.id} className="glass-panel rounded-2xl p-6 border border-cinemax-border space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${src.is_enabled ? "bg-emerald-400 shadow-sm shadow-emerald-400/50" : "bg-slate-600"}`} />
                  <h4 className="text-lg font-bold text-white">{src.provider_name}</h4>
                  <span className="uppercase text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {src.provider_type}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs">
                  <span className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono">
                    {src.cost_status}
                  </span>
                  <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono">
                    {src.access_method}
                  </span>
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase">Authentication Requirement:</span>
                  <span className="text-white font-medium">{src.auth_requirement}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase">Rate Limit Etiquette:</span>
                  <span className="text-white font-mono">{src.rate_limit_info}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase">Last Synchronization:</span>
                  <span className="text-slate-300 font-mono">
                    {src.last_sync ? new Date(src.last_sync).toLocaleString() : "Never"}
                  </span>
                </div>
              </div>

              {/* Attribution and License */}
              <div className="bg-slate-900/90 rounded-xl p-3.5 border border-slate-800/80 space-y-1.5 text-xs">
                <div className="text-slate-400 font-medium">Attribution:</div>
                <p className="text-slate-300 italic">{src.attribution_text}</p>
                <div className="pt-1 flex items-center justify-between text-[11px]">
                  <a
                    href={src.license_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
                  >
                    View Official Terms / License <ExternalLink className="w-3 h-3" />
                  </a>
                  <span className="text-slate-500">{src.data_retention_rules}</span>
                </div>
              </div>

              {/* Limitations or Errors */}
              {src.last_error && (
                <div className="p-3 rounded-xl bg-ruby/10 border border-ruby/20 text-ruby text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <span>Reported Error / Limitation: {src.last_error}</span>
                </div>
              )}

              <div className="text-[11px] text-slate-400">
                <strong>Coverage Limitations:</strong> {src.coverage_limitations}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
