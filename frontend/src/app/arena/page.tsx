"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Trophy, Sparkles, Lock, Clock, CheckCircle2, AlertCircle,
  HelpCircle, ArrowRight, Award, User
} from "lucide-react";
import {
  fetchTitles, fetchTitleDetail, submitArenaGuess,
  fetchUserGuesses, fetchLeaderboard, TitleSummary
} from "@/lib/api";

function ArenaContent() {
  const searchParams = useSearchParams();
  const preselectedTitleId = searchParams.get("title_id");

  const [titles, setTitles] = useState<TitleSummary[]>([]);
  const [selectedTitleId, setSelectedTitleId] = useState<string>("");
  const [selectedTitle, setSelectedTitle] = useState<any>(null);
  const [guessValue, setGuessValue] = useState<number>(50);
  const [userGuesses, setUserGuesses] = useState<any[]>([]);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    setLoadError(null);
    fetchTitles({ limit: 100 })
      .then((data) => {
        setTitles(data);
        if (preselectedTitleId && data.some((t) => t.id === preselectedTitleId)) {
          setSelectedTitleId(preselectedTitleId);
        } else if (data.length > 0) {
          setSelectedTitleId(data[0].id);
        }
      })
      .catch((err) => {
        setLoadError(err.message || "Failed to load titles from the backend service.");
      });

    loadUserData();
  }, [preselectedTitleId]);

  useEffect(() => {
    if (selectedTitleId) {
      fetchTitleDetail(selectedTitleId).then((t) => {
        setSelectedTitle(t);
        if (t?.current_popularity_score) {
          setGuessValue(Math.round(t.current_popularity_score));
        }
      });
    }
  }, [selectedTitleId]);

  async function loadUserData() {
    const guesses = await fetchUserGuesses("arena_player_1");
    setUserGuesses(guesses);
    const lead = await fetchLeaderboard();
    setLeaderboard(lead);
  }

  async function handleSubmitGuess(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedTitleId) return;

    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    try {
      await submitArenaGuess({
        title_id: selectedTitleId,
        predicted_score: guessValue,
        user_session_id: "arena_player_1",
      });
      setSubmitSuccess(`Your prediction of ${guessValue} for "${selectedTitle?.canonical_title}" is officially locked!`);
      loadUserData();
    } catch (err: any) {
      setSubmitError(err.message || "Failed to submit prediction");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-10">
      {/* Header Banner */}
      <div className="relative rounded-2xl overflow-hidden bg-gradient-to-r from-amber-950/40 via-slate-900 to-indigo-950/40 border border-yellow-500/20 p-8 shadow-xl">
        <div className="max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 text-xs font-semibold">
            <Trophy className="w-3.5 h-3.5" />
            Interactive Popularity Guessing Arena
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
            Cinemax Prediction Arena
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed">
            Test your entertainment intuition! Guess where a movie, anime, or series' popularity score will land after 7 days. Once submitted, guesses are permanently locked until the target window is evaluated.
          </p>
        </div>
      </div>

      {loadError && (
        <div className="glass-panel p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-200 text-xs flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>
              <strong>Backend Service Notice:</strong> {loadError}. Ensure the backend service is running to fetch titles and submit guesses.
            </span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Game Form (Left 2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          <form onSubmit={handleSubmitGuess} className="glass-panel rounded-2xl p-6 md:p-8 border border-cinemax-border space-y-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-yellow-400" />
              Lock in Your 7-Day Forecast
            </h2>

            {/* Title Selector */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                1. Select Entertainment Title:
              </label>
              <select
                value={selectedTitleId}
                onChange={(e) => setSelectedTitleId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-yellow-400"
              >
                {titles.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.canonical_title} ({t.type.replace("_", " ")}, Pop: {t.current_popularity_score?.toFixed(1)})
                  </option>
                ))}
              </select>
            </div>

            {/* Current Score Display */}
            {selectedTitle && (
              <div className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-400 block">Current Measured Popularity:</span>
                  <div className="text-2xl font-black text-blue-400 font-mono mt-0.5">
                    {selectedTitle.current_popularity_score?.toFixed(1)} <span className="text-xs text-slate-500 font-normal">/ 100</span>
                  </div>
                </div>
                <div className="text-right text-xs text-slate-400">
                  <span>Release Year: <strong className="text-white">{selectedTitle.release_year || "TBA"}</strong></span>
                  <span className="block mt-0.5 capitalize text-slate-300">{selectedTitle.content_status}</span>
                </div>
              </div>
            )}

            {/* Guess Slider */}
            <div className="space-y-4 pt-2">
              <div className="flex justify-between items-center">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  2. Your 7-Day Predicted Popularity (0 - 100):
                </label>
                <span className="text-2xl font-black text-yellow-400 font-mono">
                  {guessValue}
                </span>
              </div>

              <input
                type="range"
                min="0"
                max="100"
                step="1"
                value={guessValue}
                onChange={(e) => setGuessValue(Number(e.target.value))}
                className="w-full accent-yellow-400 cursor-pointer h-2 bg-slate-800 rounded-lg"
              />

              <div className="flex justify-between text-[11px] text-slate-500 font-mono">
                <span>0 (Inactive)</span>
                <span>50 (Moderate)</span>
                <span>100 (Global Phenomenon)</span>
              </div>
            </div>

            {/* Horizon & Lock Notice */}
            <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800/80 space-y-2 text-xs text-slate-300">
              <div className="flex items-center gap-2 font-semibold text-white">
                <Lock className="w-4 h-4 text-yellow-400" />
                Prediction Horizon: 7 Days (Target Window)
              </div>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Upon clicking "Submit & Lock Prediction", your guess is permanently recorded and locked against alteration. Points are calculated as: <code>Points = max(0, 100 - |Guess - Actual| × 3)</code> when the 7-day period concludes.
              </p>
            </div>

            {submitSuccess && (
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                {submitSuccess}
              </div>
            )}

            {submitError && (
              <div className="p-3.5 rounded-xl bg-ruby/10 border border-ruby/20 text-ruby text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {submitError}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-yellow-400 hover:bg-yellow-300 disabled:opacity-50 text-slate-950 font-bold py-3.5 px-6 rounded-xl text-sm transition-all shadow-lg flex items-center justify-center gap-2"
            >
              <Lock className="w-4 h-4" />
              {submitting ? "Locking Guess..." : "Submit & Lock Prediction"}
            </button>
          </form>

          {/* User Active & Past Guesses Table */}
          <div className="glass-panel rounded-2xl p-6 border border-cinemax-border space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-blue-400" />
              Your Prediction Log ({userGuesses.length} Recorded)
            </h3>

            {userGuesses.length === 0 ? (
              <p className="text-slate-400 text-xs py-4">You have not submitted any predictions yet. Lock your first guess above!</p>
            ) : (
              <div className="divide-y divide-slate-800/80">
                {userGuesses.map((g) => (
                  <div key={g.id} className="py-3 flex items-center justify-between gap-4 text-xs">
                    <div>
                      <div className="font-semibold text-white">{g.canonical_title || "Entertainment Title"}</div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
                        <span>Baseline: {g.baseline_score_at_guess}</span>
                        <span>•</span>
                        <span>Target: {new Date(g.target_date).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="font-mono text-yellow-400 font-bold">
                        Guessed: {g.predicted_score}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase flex items-center gap-1 justify-end">
                        <Lock className="w-3 h-3 text-slate-400" />
                        {g.actual_score !== null ? (
                          <span className="text-emerald-400 font-bold">Score: {g.accuracy_points} pts</span>
                        ) : (
                          <span>Locked (Active)</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Community Leaderboard (Right 1 col) */}
        <div className="space-y-6">
          <div className="glass-panel rounded-2xl p-6 border border-cinemax-border space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
              <Award className="w-5 h-5 text-yellow-400" />
              <h3 className="font-bold text-white text-base">Prediction Leaderboard</h3>
            </div>

            <p className="text-slate-400 text-xs leading-relaxed">
              Top entertainment predictors ranked by cumulative accuracy points.
            </p>

            <div className="divide-y divide-slate-800/80">
              <div className="py-2.5 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-yellow-400 text-slate-950 font-bold text-[10px] flex items-center justify-center">1</span>
                  <span className="text-white font-medium">arena_player_1</span>
                </div>
                <span className="font-mono font-bold text-emerald-400">97.0 pts</span>
              </div>
              <div className="py-2.5 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-700 text-white font-bold text-[10px] flex items-center justify-center">2</span>
                  <span className="text-slate-300 font-medium">cine_prophet</span>
                </div>
                <span className="font-mono font-bold text-slate-300">92.5 pts</span>
              </div>
              <div className="py-2.5 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-amber-800 text-white font-bold text-[10px] flex items-center justify-center">3</span>
                  <span className="text-slate-300 font-medium">anime_radar</span>
                </div>
                <span className="font-mono font-bold text-slate-300">88.0 pts</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ArenaPage() {
  return (
    <Suspense fallback={<div className="py-24 text-center text-slate-400 font-mono text-sm">Loading Cinemax Prediction Arena...</div>}>
      <ArenaContent />
    </Suspense>
  );
}
