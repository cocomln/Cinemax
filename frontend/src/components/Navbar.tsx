"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Activity, Compass, TrendingUp, Trophy, Database, RefreshCw } from "lucide-react";
import { fetchRefreshStatus, RefreshStatus } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [refreshInfo, setRefreshInfo] = useState<RefreshStatus | null>(null);

  useEffect(() => {
    fetchRefreshStatus().then(setRefreshInfo);
  }, []);

  const navLinks = [
    { name: "Intelligence", href: "/", icon: Activity },
    { name: "Explore", href: "/explore", icon: Compass },
    { name: "Predictions", href: "/#predictions", icon: TrendingUp },
    { name: "Prediction Arena", href: "/arena", icon: Trophy },
    { name: "Source Registry", href: "/sources", icon: Database },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-cinemax-border/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-black text-white text-xl tracking-wider shadow-md group-hover:scale-105 transition-transform">
            C
          </div>
          <div>
            <span className="font-bold text-xl tracking-tight text-white flex items-center gap-1">
              CINEMAX
              <span className="text-[10px] uppercase font-semibold tracking-widest px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                INTEL
              </span>
            </span>
          </div>
        </Link>

        {/* Navigation items */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "text-blue-400 bg-blue-500/10 border border-blue-500/20"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Refresh Badge */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 text-xs bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-full text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Midnight IST Refresh:</span>
            <span className="text-emerald-400 font-mono">
              {refreshInfo?.last_successful_refresh_ist || "12:00 AM IST"}
            </span>
          </div>

          <Link
            href="/arena"
            className="flex items-center gap-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-lg shadow-sm transition-all"
          >
            <Trophy className="w-3.5 h-3.5 text-yellow-300" />
            Arena Game
          </Link>
        </div>
      </div>
    </header>
  );
}
