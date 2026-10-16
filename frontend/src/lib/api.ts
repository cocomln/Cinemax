const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== "undefined" ? "/api" : "http://localhost:8000/api");

export interface TitleSummary {
  id: string;
  canonical_title: string;
  original_title: string | null;
  type: string;
  original_language: string | null;
  release_date: string | null;
  release_year: number | null;
  genres: string[];
  content_status: string;
  poster_url: string | null;
  backdrop_url: string | null;
  current_popularity_score: number;
  popularity_growth_velocity: number;
  popularity_source_coverage: number;
  formatted_runtime: string | null;
}

export interface RatingItem {
  id: string;
  source_name: string;
  rating_value: number;
  max_rating: number;
  normalized_value: number;
  vote_count: number | null;
  rating_type: string;
  source_url: string | null;
  collected_at: string;
}

export interface EpisodeItem {
  id: string;
  season_number: number | null;
  episode_number: number;
  absolute_episode_number: number | null;
  episode_title: string | null;
  release_date: string | null;
  runtime_minutes: number | null;
  is_special: boolean;
  source: string;
}

export interface HistoricalObs {
  metric_name: string;
  metric_value: number;
  observation_window: string;
  timestamp: string;
  source: string;
  confidence: number;
  data_quality_status: string;
}

export interface TitleDetail extends TitleSummary {
  synopsis: string | null;
  country: string | null;
  franchise: string | null;
  official_website: string | null;
  runtime_minutes: number | null;
  runtime_source: string | null;
  runtime_verification_status: string | null;
  alternative_titles: string[];
  source_identifiers: Record<string, any>;
  metadata_completeness: number;
  announced_episodes: number | null;
  released_episodes: number | null;
  known_total_episodes: number | null;
  estimated_total_episodes: number | null;
  unknown_total_episodes: boolean;
  ratings: RatingItem[];
  episodes: EpisodeItem[];
  historical_observations: HistoricalObs[];
  latest_prediction: {
    id: string;
    horizon_days: number;
    current_score: number;
    predicted_score: number;
    predicted_change: number;
    uncertainty_lower: number | null;
    uncertainty_upper: number | null;
    model_version: string;
    contributing_factors: Record<string, number>;
    generated_at: string;
  } | null;
  popularity_breakdown: {
    total_score: number;
    recent_volume_score: number;
    growth_velocity_score: number;
    engagement_score: number;
    source_breadth_score: number;
    sustained_activity_score: number;
    source_coverage: number;
    has_sufficient_data: boolean;
    status_label: string;
  } | null;
}

export interface SourceEntry {
  id: string;
  provider_name: string;
  provider_type: string;
  supported_fields: string[];
  access_method: string;
  auth_requirement: string;
  cost_status: string;
  license_url: string;
  attribution_text: string;
  rate_limit_info: string;
  data_retention_rules: string;
  is_enabled: boolean;
  last_sync: string | null;
  last_error: string | null;
  coverage_limitations: string;
}

export interface RefreshStatus {
  status: string;
  message: string;
  last_successful_refresh_ist: string;
  last_successful_refresh_utc: string;
  total_titles: number;
  active_sources: string[];
}

export async function fetchTitles(params?: {
  type?: string;
  status?: string;
  year_from?: number;
  year_to?: number;
  genre?: string;
  search?: string;
  sort_by?: string;
  limit?: number;
}): Promise<TitleSummary[]> {
  const query = new URLSearchParams();
  if (params?.type) query.append("type", params.type);
  if (params?.status) query.append("status", params.status);
  if (params?.year_from) query.append("year_from", params.year_from.toString());
  if (params?.year_to) query.append("year_to", params.year_to.toString());
  if (params?.genre) query.append("genre", params.genre);
  if (params?.search) query.append("search", params.search);
  if (params?.sort_by) query.append("sort_by", params.sort_by);
  if (params?.limit) query.append("limit", params.limit.toString());

  try {
    const res = await fetch(`${API_BASE_URL}/titles?${query.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch titles");
    return res.json();
  } catch (e) {
    console.error("API error fetchTitles:", e);
    return [];
  }
}

export async function fetchTrending(limit = 10): Promise<TitleSummary[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/titles/trending?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch trending");
    return res.json();
  } catch (e) {
    return [];
  }
}

export async function fetchBreakouts(limit = 10): Promise<TitleSummary[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/titles/breakouts?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch breakouts");
    return res.json();
  } catch (e) {
    return [];
  }
}

export async function fetchUpcoming(limit = 10): Promise<TitleSummary[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/titles/upcoming?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch upcoming");
    return res.json();
  } catch (e) {
    return [];
  }
}

export async function fetchTitleDetail(id: string): Promise<TitleDetail | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/titles/${id}`);
    if (!res.ok) throw new Error("Failed to fetch title detail");
    return res.json();
  } catch (e) {
    console.error("API error fetchTitleDetail:", e);
    return null;
  }
}

export async function fetchPredictions(sortBy = "predicted_change"): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/predictions?sort_by=${sortBy}&limit=25`);
    if (!res.ok) throw new Error("Failed to fetch predictions");
    return res.json();
  } catch (e) {
    return [];
  }
}

export async function fetchSourceRegistry(): Promise<SourceEntry[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/sources`);
    if (!res.ok) throw new Error("Failed to fetch sources");
    return res.json();
  } catch (e) {
    return [];
  }
}

export async function fetchRefreshStatus(): Promise<RefreshStatus | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/refresh/status`);
    if (!res.ok) throw new Error("Failed to fetch refresh status");
    return res.json();
  } catch (e) {
    return null;
  }
}

export async function triggerRefresh(): Promise<any> {
  try {
    const res = await fetch(`${API_BASE_URL}/refresh/trigger`, { method: "POST" });
    return res.json();
  } catch (e) {
    return { error: String(e) };
  }
}

export async function submitArenaGuess(data: {
  title_id: string;
  predicted_score: number;
  user_session_id?: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/arena/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...data,
      user_session_id: data.user_session_id || "arena_player_1"
    })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Submission failed");
  }
  return res.json();
}

export async function fetchUserGuesses(sessionId = "arena_player_1"): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/arena/guesses?user_session_id=${sessionId}`);
    if (!res.ok) return [];
    return res.json();
  } catch (e) {
    return [];
  }
}

export async function fetchLeaderboard(): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/arena/leaderboard`);
    if (!res.ok) return [];
    return res.json();
  } catch (e) {
    return [];
  }
}
