import re

# Comprehensive lexicon of sentiment words tailored to entertainment, film, anime & television reviews
POSITIVE_WORDS = {
    "masterpiece", "brilliant", "phenomenal", "stellar", "exceptional", "superb",
    "stunning", "fantastic", "amazing", "great", "excellent", "loved", "love",
    "captivating", "gripping", "compelling", "must-watch", "hype", "hyped",
    "underrated", "peak", "epic", "cinematic", "flawless", "breathtaking",
    "top-tier", "goat", "wholesome", "charming", "entertaining", "solid",
    "engaging", "hilarious", "emotional", "touching", "thrilling", "genius"
}

NEGATIVE_WORDS = {
    "terrible", "horrible", "awful", "trash", "disappointing", "disappointment",
    "boring", "slow", "dull", "overrated", "unwatchable", "flop", "ruined",
    "bad", "worst", "cringe", "flat", "cliche", "plot-hole", "waste", "poor",
    "mess", "pointless", "lazy", "forgettable", "annoying", "mid", "fell off",
    "dragged", "cheap", "incoherent", "underwhelming", "abysmal", "tedious"
}

NEGATION_WORDS = {"not", "never", "no", "hardly", "barely", "scarcely", "without", "isnt", "wasnt", "arent"}
INTENSIFIERS = {"very", "really", "extremely", "absolutely", "insanely", "incredibly", "truly"}

class LocalSentimentAnalyzer:
    """Zero-cost local rule-based sentiment analyzer for entertainment discussions."""

    @staticmethod
    def analyze_text(text: str) -> dict[str, float]:
        if not text or not text.strip():
            return {"positive": 0.0, "neutral": 1.0, "negative": 0.0, "compound": 0.0}

        tokens = re.findall(r"\b[a-zA-Z'\-]+\b", text.lower())
        if not tokens:
            return {"positive": 0.0, "neutral": 1.0, "negative": 0.0, "compound": 0.0}

        pos_score = 0.0
        neg_score = 0.0
        n_tokens = len(tokens)

        for i, word in enumerate(tokens):
            multiplier = 1.0
            # Lookback for intensifier
            if i > 0 and tokens[i - 1] in INTENSIFIERS:
                multiplier = 1.6

            # Lookback for negation
            is_negated = False
            if i > 0 and tokens[i - 1] in NEGATION_WORDS:
                is_negated = True
            elif i > 1 and tokens[i - 2] in NEGATION_WORDS:
                is_negated = True

            if word in POSITIVE_WORDS:
                if is_negated:
                    neg_score += 1.0 * multiplier
                else:
                    pos_score += 1.0 * multiplier
            elif word in NEGATIVE_WORDS:
                if is_negated:
                    pos_score += 0.8 * multiplier
                else:
                    neg_score += 1.0 * multiplier

        total_emotional = pos_score + neg_score
        if total_emotional == 0:
            return {"positive": 0.0, "neutral": 1.0, "negative": 0.0, "compound": 0.0}

        # Normalize to ratios
        pos_ratio = pos_score / (total_emotional + 2.0)
        neg_ratio = neg_score / (total_emotional + 2.0)
        neu_ratio = max(0.0, 1.0 - (pos_ratio + neg_ratio))

        # Compound score between -1.0 and +1.0
        compound = (pos_score - neg_score) / (pos_score + neg_score + 1.0)

        return {
            "positive": round(pos_ratio, 3),
            "neutral": round(neu_ratio, 3),
            "negative": round(neg_ratio, 3),
            "compound": round(compound, 3)
        }

analyzer = LocalSentimentAnalyzer()
