import math
from app.core.config import settings

class PopularityScoringEngine:
    """
    Transparent, reproducible 0 to 100 Popularity Scoring Engine.
    Measures public popularity and attention volume, NOT artistic quality.
    
    Formula components:
    - 30% Recent discussion volume (log-scaled)
    - 25% Growth / velocity in mentions (% change from prior window)
    - 20% Engagement per discussion (likes, comments, reposts normalized)
    - 15% Cross-source breadth (fraction of active sources with activity)
    - 10% Sustained historical activity (baseline consistency)
    """

    def __init__(
        self,
        weight_volume: float = settings.WEIGHT_RECENT_VOLUME,
        weight_growth: float = settings.WEIGHT_GROWTH_VELOCITY,
        weight_engagement: float = settings.WEIGHT_ENGAGEMENT,
        weight_breadth: float = settings.WEIGHT_SOURCE_BREADTH,
        weight_sustained: float = settings.WEIGHT_SUSTAINED_ACTIVITY,
    ):
        self.w_vol = weight_volume
        self.w_growth = weight_growth
        self.w_eng = weight_engagement
        self.w_breadth = weight_breadth
        self.w_sust = weight_sustained

    def calculate_popularity(
        self,
        recent_mentions: int,
        prior_mentions: int,
        total_engagements: int,
        active_sources_count: int,
        total_possible_sources: int = 4, # e.g. AniList/TVmaze, Reddit, X, Web
        historical_consistency_ratio: float = 0.5, # 0.0 to 1.0
    ) -> dict:
        """
        Compute transparent 0-100 score with component sub-scores and data sufficiency check.
        """
        # Missing data policy:
        total_activity = recent_mentions + prior_mentions + total_engagements
        if total_activity == 0 and active_sources_count == 0:
            return {
                "total_score": 0.0,
                "recent_volume_score": 0.0,
                "growth_velocity_score": 0.0,
                "engagement_score": 0.0,
                "source_breadth_score": 0.0,
                "sustained_activity_score": 0.0,
                "source_coverage": 0.0,
                "has_sufficient_data": False,
                "status_label": "Insufficient data"
            }

        # 1. Recent Volume Score (0 - 100): Log-scaled against benchmark (5,000 mentions = 100)
        # Using log1p dampens extreme outlier dominance while rewarding genuine high-volume titles.
        benchmark_vol = 5000.0
        s_vol = min(100.0, (math.log1p(recent_mentions) / math.log1p(benchmark_vol)) * 100.0)

        # 2. Growth Velocity Score (0 - 100):
        # Baseline = 50.0 (stable). Double = 80+. Half = 20.
        if prior_mentions > 0:
            growth_rate = (recent_mentions - prior_mentions) / float(prior_mentions)
            # Clip growth rate between -1.0 (-100%) and +2.0 (+200%)
            clipped_growth = max(-1.0, min(2.0, growth_rate))
            s_growth = 50.0 + (clipped_growth * 25.0)
        elif recent_mentions > 0:
            # New breakout title
            s_growth = 75.0
        else:
            s_growth = 10.0
        s_growth = max(0.0, min(100.0, s_growth))

        # 3. Engagement Score (0 - 100):
        # Ratio of engagements per mention (benchmark = 10 engagements per mention)
        eng_ratio = total_engagements / max(1.0, float(recent_mentions))
        s_eng = min(100.0, (math.log1p(eng_ratio) / math.log1p(15.0)) * 100.0)

        # 4. Cross-Source Breadth (0 - 100):
        effective_possible = max(1, total_possible_sources)
        coverage_ratio = min(1.0, active_sources_count / float(effective_possible))
        s_breadth = coverage_ratio * 100.0

        # 5. Sustained Activity Baseline (0 - 100):
        s_sust = max(0.0, min(100.0, historical_consistency_ratio * 100.0))

        # Weighted combination
        raw_score = (
            (self.w_vol * s_vol) +
            (self.w_growth * s_growth) +
            (self.w_eng * s_eng) +
            (self.w_breadth * s_breadth) +
            (self.w_sust * s_sust)
        )
        total_score = round(max(0.0, min(100.0, raw_score)), 1)

        # Status label
        if total_score >= 75.0 and s_growth >= 65.0:
            status_label = "Trending High"
        elif total_score >= 60.0:
            status_label = "Popular"
        elif total_score >= 30.0:
            status_label = "Moderate Activity"
        else:
            status_label = "Low Activity"

        return {
            "total_score": total_score,
            "recent_volume_score": round(s_vol, 1),
            "growth_velocity_score": round(s_growth, 1),
            "engagement_score": round(s_eng, 1),
            "source_breadth_score": round(s_breadth, 1),
            "sustained_activity_score": round(s_sust, 1),
            "source_coverage": round(coverage_ratio, 2),
            "has_sufficient_data": True,
            "status_label": status_label
        }

popularity_engine = PopularityScoringEngine()
