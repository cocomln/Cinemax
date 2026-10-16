import Link from "next/link";
import { ShieldCheck, Heart, ExternalLink } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-cinemax-border/80 bg-slate-950/80 mt-20 text-slate-400 text-xs py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3">
            <div className="font-bold text-white text-base tracking-wider flex items-center gap-2">
              <span className="w-6 h-6 rounded bg-blue-600 flex items-center justify-center text-xs font-black">C</span>
              CINEMAX
            </div>
            <p className="text-slate-400 leading-relaxed">
              A free, zero-cost, data-driven entertainment intelligence platform tracking movies, television series, and anime with local machine learning predictions and transparent popularity scoring.
            </p>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-medium">
              <ShieldCheck className="w-3.5 h-3.5" />
              100% Zero-Cost Budget Guaranteed
            </div>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Navigation</h4>
            <ul className="space-y-2">
              <li><Link href="/" className="hover:text-blue-400 transition-colors">Intelligence Dashboard</Link></li>
              <li><Link href="/explore" className="hover:text-blue-400 transition-colors">Catalog Explorer (1995-Present)</Link></li>
              <li><Link href="/arena" className="hover:text-blue-400 transition-colors">Prediction Arena Game</Link></li>
              <li><Link href="/sources" className="hover:text-blue-400 transition-colors">Data Source Registry</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Data Attributions</h4>
            <ul className="space-y-2">
              <li>
                <a href="https://anilist.co" target="_blank" rel="noreferrer" className="hover:text-blue-400 flex items-center gap-1">
                  AniList GraphQL API (Free Anime Catalog) <ExternalLink className="w-3 h-3 opacity-60" />
                </a>
              </li>
              <li>
                <a href="https://www.tvmaze.com/api" target="_blank" rel="noreferrer" className="hover:text-blue-400 flex items-center gap-1">
                  TVmaze API (CC BY-SA 4.0 TV Metadata) <ExternalLink className="w-3 h-3 opacity-60" />
                </a>
              </li>
              <li>
                <a href="https://www.wikidata.org" target="_blank" rel="noreferrer" className="hover:text-blue-400 flex items-center gap-1">
                  Wikidata (CC0 1.0 Universal Public Domain) <ExternalLink className="w-3 h-3 opacity-60" />
                </a>
              </li>
              <li>
                <a href="https://www.themoviedb.org" target="_blank" rel="noreferrer" className="hover:text-blue-400 flex items-center gap-1">
                  TMDB (Free Non-Commercial Metadata) <ExternalLink className="w-3 h-3 opacity-60" />
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Operational Integrity</h4>
            <p className="leading-relaxed mb-2">
              Scheduled refresh executes daily at <strong>12:00 AM IST</strong> (18:30 UTC). All popularity metrics and ratings preserve traceable provenance.
            </p>
            <p className="text-slate-500 text-[11px]">
              No paid AI models. No data fabrication. No hidden subscription feeds.
            </p>
          </div>
        </div>

        <div className="border-t border-slate-900 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500">
          <p>© 2026 Cinemax Platform. Open-source under MIT License.</p>
          <p className="flex items-center gap-1">
            Engineered for entertainment fans & data enthusiasts
          </p>
        </div>
      </div>
    </footer>
  );
}
