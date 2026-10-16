"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Search, Filter, Compass, ArrowUpRight, ArrowDownRight, Film, Tv, PlayCircle } from "lucide-react";
import { fetchTitles, TitleSummary } from "@/lib/api";

export default function ExplorePage() {
  const [titles, setTitles] = useState<TitleSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [yearFrom, setYearFrom] = useState<number>(1995);
  const [sortBy, setSortBy] = useState<string>("popularity");

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await fetchTitles({
          type: selectedType === "all" ? undefined : selectedType,
          status: selectedStatus === "all" ? undefined : selectedStatus,
          year_from: yearFrom,
          search: search || undefined,
          sort_by: sortBy,
          limit: 100,
        });
        setTitles(data);
      } finally {
        setLoading(false);
      }
    }
    const timer = setTimeout(() => {
      load();
    }, 250);
    return () => clearTimeout(timer);
  }, [selectedType, selectedStatus, yearFrom, search, sortBy]);

  return (
    <div className="space-y-8">
      {/* Explorer Header */}
      <div className="border-b border-cinemax-border pb-6 space-y-2">
        <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
          <Compass className="w-8 h-8 text-blue-500" />
          Entertainment Catalog Explorer
        </h1>
        <p className="text-slate-400 text-sm max-w-2xl">
          Multi-source database covering movies, TV series, and anime from January 1, 1995 to latest releases and announced titles.
        </p>
      </div>

      {/* Filter and Search Controls */}
      <div className="glass-panel rounded-xl p-5 border border-cinemax-border space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by title, original title, or aliases..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-800">
          {/* Category */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 font-semibold mr-1">Category:</span>
            {[
              { id: "all", label: "All" },
              { id: "movie", label: "Movies" },
              { id: "tv", label: "TV Series" },
              { id: "anime", label: "Anime" },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedType(t.id)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  selectedType === t.id
                    ? "bg-blue-600 text-white"
                    : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Status */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 font-semibold mr-1">Status:</span>
            {[
              { id: "all", label: "All" },
              { id: "released", label: "Released" },
              { id: "ongoing", label: "Ongoing" },
              { id: "upcoming", label: "Upcoming" },
            ].map((s) => (
              <button
                key={s.id}
                onClick={() => setSelectedStatus(s.id)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  selectedStatus === s.id
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>

          {/* Sort By */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400 font-semibold">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="popularity">Popularity Score</option>
              <option value="velocity">Growth Velocity</option>
              <option value="release_date">Release Date</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="text-xs text-slate-400 font-mono">
        Showing <strong>{titles.length}</strong> matching titles
      </div>

      {/* Grid */}
      {loading ? (
        <div className="py-20 text-center text-slate-400 text-sm">Loading titles catalog...</div>
      ) : titles.length === 0 ? (
        <div className="py-20 text-center text-slate-400 text-sm">
          No entertainment titles found matching your search criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {titles.map((title) => (
            <Link
              key={title.id}
              href={`/title/${title.id}`}
              className="glass-panel group rounded-xl overflow-hidden hover:border-blue-500/50 hover:shadow-xl transition-all flex flex-col"
            >
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

                <div className="absolute top-2.5 right-2.5 bg-slate-950/90 backdrop-blur-md border border-slate-700/80 px-2.5 py-1 rounded-lg text-xs font-mono font-bold text-blue-400">
                  Pop: <span className="text-white text-sm">{title.current_popularity_score?.toFixed(1)}</span>
                </div>

                <div className="absolute bottom-2.5 left-2.5 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider text-slate-300 uppercase">
                  {title.type.replace("_", " ")}
                </div>
              </div>

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
                  </div>
                  <span className="text-[11px] text-slate-400 truncate max-w-[120px]">
                    {title.genres.slice(0, 2).join(", ")}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
