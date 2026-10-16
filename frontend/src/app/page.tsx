"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import {
  TrendingUp, Sparkles, Film, Tv, PlayCircle, Trophy,
  ArrowUpRight, ArrowDownRight, Clock, ShieldCheck, ChevronRight
} from "lucide-react";
import {
  fetchTrending, fetchBreakouts, fetchUpcoming, fetchPredictions,
  fetchRefreshStatus, TitleSummary, RefreshStatus
} from "@/lib/api";

export default function Home() {
  const [trending, setTrending] = useState<TitleSummary[]>([]);
  const [breakouts, setBreakouts] = useState<TitleSummary[]>([]);
  const [upcoming, setUpcoming] = useState<TitleSummary[]>([]);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [trendData, breakData, upData, predData, refData] = await Promise.all([
          fetchTrending(12),
          fetchBreakouts(6),
          fetchUpcoming(6),
          fetchPredictions("predicted_change"),
          fetchRefreshStatus()
        ]);
        setTrending(trendData);
        setBreakouts(breakData);
        setUpcoming(upData);
        setPredictions(predData.slice(0, 6));
        setRefreshStatus(refData);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredTrending = trending.filter((item) => {
    if (activeCategory === "all") return true;
    if (activeCategory === "movies") return item.type === "movie" || item.type === "anime_film";
    if (activeCategory === "tv") return item.type === "tv_series";
    if (activeCategory === "anime") return item.type.includes("anime") || item.type === "ova";
    return true;
  });

  return (
    <div className="space-y-12">
      {/* Hero Banner */}
      <section className="relative rounded-2xl overflow-hidden bg-gradient-to-br from-slate-900 via-slate-900/90 to-blue-950/40 border border-cinemax-border p-8 md:p-12 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-5">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            Zero-Cost Entertainment Intelligence Platform
          </div>

          <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight">
            Track Real-World Popularity, Ratings & <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">ML Predictions</span>
          </h1>

          <p className="text-slate-300 text-base md:text-lg leading-relaxed">
            Multi-source intelligence across movies, TV series, and anime. Powered by real data provenance from AniList, TVmaze, Wikidata CC0, and local Scikit-Learn forecasts.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              href="/explore"
              className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-xl shadow-lg shadow-blue-600/25 transition-all flex items-center gap-2 text-sm"
            >
              Explore Catalog (1995-Present)
              <ChevronRight className="w-4 h-4" />
            </Link>

            <Link
              href="/arena"
              className="glass-panel hover:bg-slate-800 text-slate-200 font-semibold px-6 py-3 rounded-xl transition-all flex items-center gap-2 text-sm"
            >
              <Trophy className="w-4 h-4 text-yellow-400" />
              Play Prediction Arena
            </Link>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-slate-800/80">
            <div>
              <div className="text-2xl font-black text-white font-mono">
                {refreshStatus?.total_titles || 65}+
              </div>
              <div className="text-xs text-slate-400">Verified Titles</div>
            </div>
            <div>
              <div className="text-2xl font-black text-blue-400 font-mono">750+</div>
              <div className="text-xs text-slate-400">Tracked Episodes</div>
            </div>
            <div>
              <div className="text-2xl font-black text-emerald-400 font-mono">0 - 100</div>
              <div className="text-xs text-slate-400">Transparent Score</div>
            </div>
            <div>
              <div className="text-2xl font-black text-indigo-400 font-mono">7-Day</div>
              <div className="text-xs text-slate-400">Local ML Forecast</div>
            </div>
          </div>
        </div>
      </section>

      {/* Category Tabs & Popularity Leaderboard */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cinemax-border pb-4">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-400" />
              Measured Popularity Ranking
            </h2>
            <p className="text-slate-400 text-xs">
              0–100 scale measuring volume, velocity, engagement, and cross-source breadth (not artistic quality).
            </p>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-xl border border-cinemax-border text-xs">
            {[
              { id: "all", label: "All Entertainment" },
              { id: "movies", label: "Movies", icon: Film },
              { id: "tv", label: "TV Series", icon: Tv },
              { id: "anime", label: "Anime", icon: PlayCircle }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveCategory(tab.id)}
                className={`px-3.5 py-1.5 rounded-lg font-medium transition-colors ${
                  activeCategory === tab.id
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Titles Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredTrending.map((title) => (
            <Link
              key={title.id}
              href={`/title/${title.id}`}
              className="glass-panel group rounded-xl overflow-hidden hover:border-blue-500/50 hover:shadow-xl transition-all flex flex-col"
            >
              {/* Poster frame */}
              <div className="relative aspect-[2/3] bg-slate-950 overflow-hidden">
                {title.poster_url ? (
                  <img
                    src={title.poster_url}
                    alt={title.canonical_title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-600 text-xs font-mono">
                    No Poster Available
                  </div>
                )}

                {/* Score pill */}
                <div className="absolute top-2.5 right-2.5 bg-slate-950/90 backdrop-blur-md border border-slate-700/80 px-2.5 py-1 rounded-lg text-xs font-mono font-bold text-blue-400 flex items-center gap-1">
                  <span>Pop:</span>
                  <span className="text-white text-sm">{title.current_popularity_score?.toFixed(1)}</span>
                </div>

                {/* Type badge */}
                <div className="absolute bottom-2.5 left-2.5 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider text-slate-300 uppercase">
                  {title.type.replace("_", " ")}
                </div>
              </div>

              {/* Title Content */}
              <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                <div>
                  <h3 className="font-bold text-white text-base line-clamp-1 group-hover:text-blue-400 transition-colors">
                    {title.canonical_title}
                  </h3>
                  <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                    <span>{title.release_year || "TBA"}</span>
                    {title.formatted_runtime && (
                      <>
                        <span>•</span>
                        <span>{title.formatted_runtime}</span>
                      </>
                    )}
                    <span>•</span>
                    <span className="capitalize">{title.content_status}</span>
                  </div>
                </div>

                {/* Velocity and genres */}
                <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80">
                  <div className="flex items-center gap-1 font-mono text-xs">
                    {title.popularity_growth_velocity >= 0 ? (
                      <span className="text-emerald-400 flex items-center">
                        <ArrowUpRight className="w-3.5 h-3.5" />
                        +{title.popularity_growth_velocity.toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-ruby flex items-center">
                        <ArrowDownRight className="w-3.5 h-3.5" />
                        {title.popularity_growth_velocity.toFixed(1)}%
                      </span>
                    )}
                    <span className="text-slate-500 text-[10px]">vel</span>
                  </div>

                  <span className="text-[11px] text-slate-400 truncate max-w-[120px]">
                    {title.genres.slice(0, 2).join(", ")}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 7-Day ML Prediction Spotlight */}
      <section id="predictions" className="space-y-6 pt-6">
        <div className="flex items-center justify-between border-b border-cinemax-border pb-4">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-indigo-400" />
              7-Day Machine Learning Forecasts
            </h2>
            <p className="text-slate-400 text-xs">
              Scikit-Learn time-aware models projecting 7-day future popularity trends and key contributing drivers.
            </p>
          </div>
          <Link href="/explore" className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1">
            View All Predictions <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {predictions.map((p) => {
            const isRising = p.predicted_change >= 0;
            return (
              <div key={p.id} className="glass-panel rounded-xl p-5 border border-cinemax-border space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      {p.type.replace("_", " ")}
                    </span>
                    <h4 className="font-bold text-white text-base mt-2 line-clamp-1">
                      {p.canonical_title}
                    </h4>
                  </div>
                  <div className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold flex items-center gap-1 ${
                    isRising ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-ruby/10 text-ruby border border-ruby/20"
                  }`}>
                    {isRising ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                    {isRising ? `+${p.predicted_change.toFixed(1)}` : p.predicted_change.toFixed(1)}
                  </div>
                </div>

                {/* Score Projection Visual */}
                <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800 space-y-2">
                  <div className="flex justify-between items-center text-xs font-mono">
                    <span className="text-slate-400">Current: <strong className="text-white">{p.current_score.toFixed(1)}</strong></span>
                    <span className="text-indigo-400 font-bold">Predicted (7d): <strong className="text-white text-sm">{p.predicted_score.toFixed(1)}</strong></span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full transition-all"
                      style={{ width: `${Math.min(100, Math.max(0, p.predicted_score))}%` }}
                    />
                  </div>
                  <div className="text-[11px] text-slate-400 flex justify-between">
                    <span>Uncertainty Margin:</span>
                    <span className="font-mono text-slate-300">[{p.uncertainty_lower?.toFixed(1)} - {p.uncertainty_upper?.toFixed(1)}]</span>
                  </div>
                </div>

                {/* Top Factor Attribution */}
                <div className="space-y-1 text-xs">
                  <div className="text-slate-400 font-medium text-[11px]">Key Contributing Drivers:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {Object.entries(p.contributing_factors || {}).map(([factor, val]) => {
                      const numVal = Number(val);
                      return (
                        <span key={factor} className="px-2 py-0.5 rounded bg-slate-800 text-[11px] text-slate-300 border border-slate-700">
                          {factor}: <strong className={numVal >= 0 ? "text-emerald-400" : "text-ruby"}>{numVal >= 0 ? `+${numVal}` : numVal}</strong>
                        </span>
                      );
                    })}
                  </div>
                </div>

                <Link
                  href={`/title/${p.title_id}`}
                  className="block text-center text-xs font-semibold text-blue-400 hover:text-blue-300 pt-2 border-t border-slate-800"
                >
                  View Full Title Intelligence →
                </Link>
              </div>
            );
          })}
        </div>
      </section>

      {/* Upcoming Radar & Prediction Arena Callout */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-6">
        {/* Upcoming Radar */}
        <div className="lg:col-span-2 glass-panel rounded-xl p-6 border border-cinemax-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-white text-lg flex items-center gap-2">
              <Clock className="w-5 h-5 text-gold" />
              Upcoming Releases Watchlist
            </h3>
            <span className="text-xs text-slate-400 font-mono">Announced & Future</span>
          </div>

          <div className="divide-y divide-slate-800/80">
            {upcoming.map((u) => (
              <div key={u.id} className="py-3 flex items-center justify-between gap-4">
                <div className="space-y-0.5">
                  <Link href={`/title/${u.id}`} className="font-semibold text-white hover:text-blue-400 text-sm">
                    {u.canonical_title}
                  </Link>
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span className="uppercase text-[10px] px-1.5 py-0.2 rounded bg-slate-800">{u.type.replace("_", " ")}</span>
                    <span>Release: {u.release_date || "TBA 2025/2026"}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono font-bold text-yellow-400">
                    Pop Seed: {u.current_popularity_score?.toFixed(1)}
                  </div>
                  <Link href={`/arena`} className="text-[11px] text-blue-400 hover:underline">
                    Predict in Arena →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Prediction Arena Promotion */}
        <div className="rounded-xl p-6 bg-gradient-to-br from-indigo-900/60 to-blue-900/40 border border-indigo-500/30 flex flex-col justify-between space-y-6">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-yellow-400/20 text-yellow-400 flex items-center justify-center font-bold">
              <Trophy className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">Cinemax Prediction Arena</h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              Think you know which movie, anime, or show will blow up? Predict a title's 7-day popularity score, lock in your guess, and climb the community leaderboard.
            </p>
          </div>

          <Link
            href="/arena"
            className="w-full text-center bg-yellow-400 hover:bg-yellow-300 text-slate-950 font-bold py-3 px-4 rounded-xl text-sm transition-colors shadow-lg"
          >
            Enter Prediction Arena
          </Link>
        </div>
      </section>
    </div>
  );
}
