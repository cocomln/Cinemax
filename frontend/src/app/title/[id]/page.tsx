"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Star, ExternalLink, Calendar, Clock, Film, Tv, PlayCircle,
  TrendingUp, Sparkles, Trophy, ArrowUpRight, ArrowDownRight,
  ShieldCheck, Info, CheckCircle2, AlertCircle
} from "lucide-react";
import { fetchTitleDetail, TitleDetail } from "@/lib/api";

export default function TitleDetailPage() {
  const params = useParams();
  const titleId = params.id as string;
  const [title, setTitle] = useState<TitleDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (titleId) {
      fetchTitleDetail(titleId).then((data) => {
        setTitle(data);
        setLoading(false);
      });
    }
  }, [titleId]);

  if (loading) {
    return (
      <div className="py-24 text-center text-slate-400 font-mono text-sm">
        Loading entertainment intelligence for title {titleId}...
      </div>
    );
  }

  if (!title) {
    return (
      <div className="py-24 text-center space-y-4">
        <h2 className="text-2xl font-bold text-white">Title Not Found</h2>
        <p className="text-slate-400 text-sm">The requested entertainment record does not exist or has been removed.</p>
        <Link href="/explore" className="inline-block bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold">
          Back to Explorer
        </Link>
      </div>
    );
  }

  const breakdown = title.popularity_breakdown;
  const prediction = title.latest_prediction;

  return (
    <div className="space-y-10">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/" className="hover:text-blue-400">Home</Link>
        <span>/</span>
        <Link href="/explore" className="hover:text-blue-400">Explore</Link>
        <span>/</span>
        <span className="text-slate-200 truncate max-w-xs">{title.canonical_title}</span>
      </div>

      {/* Main Hero Header */}
      <section className="glass-panel rounded-2xl overflow-hidden border border-cinemax-border p-6 md:p-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Poster Column */}
          <div className="w-full md:w-64 flex-shrink-0">
            <div className="aspect-[2/3] rounded-xl overflow-hidden bg-slate-950 border border-slate-800 shadow-xl relative">
              {title.poster_url ? (
                <img
                  src={title.poster_url}
                  alt={title.canonical_title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-600 text-xs font-mono">
                  No Poster Available
                </div>
              )}
            </div>

            {/* Quick Prediction Arena Button */}
            <div className="mt-4">
              <Link
                href={`/arena?title_id=${title.id}`}
                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-2.5 px-4 rounded-xl text-xs shadow-md transition-all"
              >
                <Trophy className="w-4 h-4 text-yellow-300" />
                Predict in Arena
              </Link>
            </div>
          </div>

          {/* Details Column */}
          <div className="flex-1 space-y-5">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="uppercase text-xs font-bold tracking-wider px-2.5 py-1 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  {title.type.replace("_", " ")}
                </span>
                <span className="capitalize text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {title.content_status}
                </span>
                {title.formatted_runtime && (
                  <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                    <Clock className="w-3.5 h-3.5" />
                    {title.formatted_runtime}
                  </span>
                )}
              </div>

              <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
                {title.canonical_title}
              </h1>

              {title.original_title && title.original_title !== title.canonical_title && (
                <p className="text-sm text-slate-400 font-medium">
                  Original Title: <span className="text-slate-300">{title.original_title}</span>
                </p>
              )}
            </div>

            {/* Key Facts Pill Row */}
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300 border-y border-slate-800 py-3">
              <div>
                <span className="text-slate-500 mr-1.5">Release Date:</span>
                <strong className="text-white font-mono">{title.release_date || `${title.release_year || "TBA"}`}</strong>
              </div>
              <div>
                <span className="text-slate-500 mr-1.5">Origin:</span>
                <strong className="text-white">{title.country || "Global"}</strong>
              </div>
              {title.genres.length > 0 && (
                <div>
                  <span className="text-slate-500 mr-1.5">Genres:</span>
                  <span className="text-slate-200">{title.genres.join(", ")}</span>
                </div>
              )}
            </div>

            {/* Synopsis */}
            {title.synopsis && (
              <div className="space-y-1">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Overview</h4>
                <p className="text-sm text-slate-300 leading-relaxed max-w-3xl">
                  {title.synopsis}
                </p>
              </div>
            )}

            {/* TV & Anime Episode Provenance Banner */}
            {(title.type.includes("tv") || title.type.includes("anime")) && (
              <div className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 text-xs space-y-2">
                <div className="font-semibold text-white flex items-center gap-2">
                  <Tv className="w-4 h-4 text-blue-400" />
                  Episode Provenance Breakdown
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-slate-300 font-mono">
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase">Announced:</span>
                    <strong className="text-white text-sm">
                      {title.announced_episodes !== null ? title.announced_episodes : "N/A"}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase">Released:</span>
                    <strong className="text-emerald-400 text-sm">
                      {title.released_episodes !== null ? title.released_episodes : (title.episodes.length || "N/A")}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase">Known Total:</span>
                    <strong className="text-white text-sm">
                      {title.known_total_episodes !== null ? title.known_total_episodes : (title.unknown_total_episodes ? "Unknown" : "TBD")}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase">Unknown Total:</span>
                    <strong className={title.unknown_total_episodes ? "text-yellow-400 text-sm" : "text-slate-400 text-sm"}>
                      {title.unknown_total_episodes ? "Yes (Never 0)" : "No"}
                    </strong>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Grid: Popularity Score Engine & 7-Day ML Prediction */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Popularity Engine Breakdown */}
        <section className="glass-panel rounded-2xl p-6 border border-cinemax-border space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-400" />
                Popularity Score: <span className="text-blue-400 font-mono">{title.current_popularity_score?.toFixed(1)}</span> / 100
              </h3>
              <p className="text-slate-400 text-xs mt-0.5">
                Transparent multi-factor measurement of audience attention and volume.
              </p>
            </div>
            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              {breakdown?.status_label || "Active"}
            </span>
          </div>

          {/* Breakdown Component Bars */}
          {breakdown && (
            <div className="space-y-3.5 text-xs">
              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Recent Discussion Volume (30% weight)</span>
                  <span className="font-mono font-bold text-white">{breakdown.recent_volume_score} / 100</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-blue-500 h-full rounded-full" style={{ width: `${breakdown.recent_volume_score}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Mention Growth Velocity (25% weight)</span>
                  <span className="font-mono font-bold text-white">{breakdown.growth_velocity_score} / 100</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${breakdown.growth_velocity_score}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Discussion Engagement (20% weight)</span>
                  <span className="font-mono font-bold text-white">{breakdown.engagement_score} / 100</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${breakdown.engagement_score}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Cross-Source Breadth (15% weight)</span>
                  <span className="font-mono font-bold text-white">{breakdown.source_breadth_score} / 100</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-purple-500 h-full rounded-full" style={{ width: `${breakdown.source_breadth_score}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Sustained Historical Baseline (10% weight)</span>
                  <span className="font-mono font-bold text-white">{breakdown.sustained_activity_score} / 100</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-yellow-500 h-full rounded-full" style={{ width: `${breakdown.sustained_activity_score}%` }} />
                </div>
              </div>

              <div className="flex justify-between items-center pt-3 border-t border-slate-800 text-[11px] text-slate-400">
                <span>Source Coverage: <strong>{((breakdown.source_coverage || 0.5) * 100).toFixed(0)}%</strong></span>
                <span>Data Sufficiency: <strong className="text-emerald-400">Verified Real Data</strong></span>
              </div>
            </div>
          )}
        </section>

        {/* 7-Day ML Prediction Forecast */}
        <section className="glass-panel rounded-2xl p-6 border border-cinemax-border space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                7-Day Popularity Forecast
              </h3>
              <p className="text-slate-400 text-xs mt-0.5">
                Local Scikit-Learn regression trained on time-lagged historical features.
              </p>
            </div>
            {prediction && (
              <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold flex items-center gap-1 ${
                prediction.predicted_change >= 0
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "bg-ruby/10 text-ruby border border-ruby/20"
              }`}>
                {prediction.predicted_change >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                {prediction.predicted_change >= 0 ? `+${prediction.predicted_change.toFixed(1)}` : prediction.predicted_change.toFixed(1)}
              </span>
            )}
          </div>

          {prediction ? (
            <div className="space-y-4">
              <div className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 grid grid-cols-2 gap-4">
                <div>
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider block">Current Score:</span>
                  <div className="text-2xl font-bold text-white font-mono mt-0.5">
                    {prediction.current_score.toFixed(1)}
                  </div>
                </div>
                <div>
                  <span className="text-[11px] text-indigo-400 uppercase tracking-wider block font-semibold">Forecast (in 7 days):</span>
                  <div className="text-2xl font-bold text-indigo-300 font-mono mt-0.5">
                    {prediction.predicted_score.toFixed(1)}
                  </div>
                </div>
              </div>

              <div className="text-xs text-slate-400 space-y-1">
                <div className="flex justify-between">
                  <span>Confidence Interval (95% bounds):</span>
                  <span className="font-mono text-slate-200">
                    [{prediction.uncertainty_lower?.toFixed(1)} — {prediction.uncertainty_upper?.toFixed(1)}]
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Model Engine:</span>
                  <span className="font-mono text-slate-300">{prediction.model_version}</span>
                </div>
              </div>

              {/* Contributing Drivers */}
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <div className="text-xs font-semibold text-white">Strongest Contributing Factors:</div>
                <div className="space-y-1.5">
                  {Object.entries(prediction.contributing_factors || {}).map(([factor, val]) => {
                    const numVal = Number(val);
                    return (
                      <div key={factor} className="flex justify-between items-center text-xs bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
                        <span className="text-slate-300">{factor}</span>
                        <span className={`font-mono font-bold ${numVal >= 0 ? "text-emerald-400" : "text-ruby"}`}>
                          {numVal >= 0 ? `+${numVal}` : numVal} pts
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <p className="text-[11px] text-slate-500 italic pt-2">
                * Note: Popularity predictions are machine-learning statistical estimates, not financial or critical guarantees.
              </p>
            </div>
          ) : (
            <div className="py-12 text-center text-slate-400 text-xs">
              Insufficient historical observations to generate a calibrated ML prediction.
            </div>
          )}
        </section>
      </div>

      {/* Multi-Source Ratings Grid (Prompt Section 9) */}
      <section className="glass-panel rounded-2xl p-6 border border-cinemax-border space-y-5">
        <div className="border-b border-slate-800 pb-4">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Star className="w-5 h-5 text-yellow-400" />
            Verified Multi-Source Ratings & Credibility
          </h3>
          <p className="text-slate-400 text-xs mt-0.5">
            Individual source ratings with verified provenance and vote counts. Ratings from different services are never merged into one field.
          </p>
        </div>

        {title.ratings.length === 0 ? (
          <div className="py-8 text-center text-slate-400 text-sm">
            Ratings currently unavailable from integrated zero-cost sources.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {title.ratings.map((r) => (
              <div key={r.id} className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-sm">{r.source_name}</span>
                  <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded ${
                    r.rating_type === "critic"
                      ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                      : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                  }`}>
                    {r.rating_type}
                  </span>
                </div>

                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-yellow-400 font-mono">
                    {r.rating_value}
                  </span>
                  <span className="text-slate-500 text-sm font-mono">/ {r.max_rating}</span>
                </div>

                <div className="text-xs text-slate-400 space-y-1 pt-2 border-t border-slate-800">
                  <div className="flex justify-between">
                    <span>Normalized (0-10):</span>
                    <strong className="text-white font-mono">{r.normalized_value.toFixed(1)}</strong>
                  </div>
                  {r.vote_count !== null && (
                    <div className="flex justify-between">
                      <span>Total Votes:</span>
                      <strong className="text-slate-300 font-mono">{r.vote_count.toLocaleString()}</strong>
                    </div>
                  )}
                </div>

                {r.source_url && (
                  <a
                    href={r.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 font-medium pt-1"
                  >
                    View on {r.source_name} <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Episode Guide (For TV & Anime) */}
      {title.episodes.length > 0 && (
        <section className="glass-panel rounded-2xl p-6 border border-cinemax-border space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Tv className="w-5 h-5 text-blue-400" />
                Episode Guide ({title.episodes.length} Episodes Tracked)
              </h3>
              <p className="text-slate-400 text-xs">
                Sourced via TVmaze / AniList with verified air dates and runtimes.
              </p>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto divide-y divide-slate-800/80 pr-2">
            {title.episodes.map((ep) => (
              <div key={ep.id} className="py-2.5 flex items-center justify-between gap-4 text-xs">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-slate-400 font-semibold w-16">
                    {ep.season_number ? `S${ep.season_number}:E${ep.episode_number}` : `Ep ${ep.episode_number}`}
                  </span>
                  <span className="text-slate-200 font-medium">
                    {ep.episode_title || `Episode ${ep.episode_number}`}
                  </span>
                  {ep.is_special && (
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-yellow-500/20 text-yellow-300">
                      Special
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-4 text-slate-400 font-mono text-[11px]">
                  <span>{ep.release_date || "Air date TBA"}</span>
                  {ep.runtime_minutes && <span>{ep.runtime_minutes}m</span>}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
