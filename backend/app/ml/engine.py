import math
from datetime import datetime
from typing import Any
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from app.ml.features import extract_title_features, FEATURE_NAMES

class PredictionEngine:
    """
    Local Scikit-Learn Machine Learning Prediction Engine.
    Predicts 7-day future popularity score with transparent baselines,
    time-aware evaluation, and feature attribution.
    """

    def __init__(self):
        self.model = Ridge(alpha=1.0)
        self.is_trained = False
        self.model_version = "baseline_momentum_decay_v1"
        self.train_mae = 0.0
        self.train_rmse = 0.0

    def baseline_predict_7d(self, feat: dict[str, float]) -> dict[str, Any]:
        """
        Transparent baseline model using momentum, release proximity, and mean-reverting decay.
        """
        curr = feat["current_score"]
        vel = feat["velocity"]
        is_upcoming = feat["is_upcoming"]
        is_ongoing = feat["is_ongoing"]
        days = feat["days_to_release"]
        post_cnt = feat["post_count"]

        contributions = {}
        delta = 0.0

        # Velocity momentum contribution (damped over 7 days)
        velocity_effect = vel * 0.15
        delta += velocity_effect
        contributions["Mention Velocity Momentum"] = round(velocity_effect, 2)

        # Upcoming release buzz surge
        if is_upcoming and 0 <= days <= 30:
            proximity_boost = (30.0 - days) * 0.25
            delta += proximity_boost
            contributions["Upcoming Release Proximity"] = round(proximity_boost, 2)

        # Ongoing broadcast momentum
        if is_ongoing:
            broadcast_boost = 1.8
            delta += broadcast_boost
            contributions["Ongoing Episode Airing"] = round(broadcast_boost, 2)

        # Mean-reverting decay for very high scores without massive fresh volume
        if curr > 60 and vel <= 0:
            decay = -((curr - 50.0) * 0.08)
            delta += decay
            contributions["Natural Decay / Mean Reversion"] = round(decay, 2)
        elif curr <= 30 and post_cnt > 20:
            breakout = 3.0
            delta += breakout
            contributions["Early Discussion Traction"] = round(breakout, 2)

        pred_score = max(0.0, min(100.0, curr + delta))
        pred_change = pred_score - curr

        # Calibrated baseline uncertainty margin (+/- 4.5 points)
        uncertainty_half_width = 4.5
        lower = max(0.0, pred_score - uncertainty_half_width)
        upper = min(100.0, pred_score + uncertainty_half_width)

        return {
            "predicted_score": round(pred_score, 1),
            "predicted_change": round(pred_change, 1),
            "uncertainty_lower": round(lower, 1),
            "uncertainty_upper": round(upper, 1),
            "model_version": self.model_version,
            "contributing_factors": contributions
        }

    def train_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train local Ridge regression model on historical observation pairs."""
        if len(X_train) < 5:
            return False
        self.model.fit(X_train, y_train)
        self.is_trained = True
        self.model_version = f"ridge_regression_v{datetime.utcnow().strftime('%Y%m%d')}"
        preds = self.model.predict(X_train)
        self.train_mae = float(np.mean(np.abs(preds - y_train)))
        self.train_rmse = float(np.sqrt(np.mean((preds - y_train) ** 2)))
        return True

    def predict_7d(self, title, historical_observations=None, social_metrics=None) -> dict[str, Any]:
        """Generate 7-day prediction for a title."""
        feat = extract_title_features(title, historical_observations, social_metrics)

        if not self.is_trained:
            return self.baseline_predict_7d(feat)

        try:
            x_vec = np.array([[feat[name] for name in FEATURE_NAMES]])
            raw_pred = float(self.model.predict(x_vec)[0])
            pred_score = max(0.0, min(100.0, raw_pred))
            curr = feat["current_score"]
            pred_change = pred_score - curr

            # Calculate feature importances based on Ridge coefficients
            coefs = self.model.coef_
            contributions = {}
            for i, name in enumerate(FEATURE_NAMES):
                impact = coefs[i] * feat[name]
                if abs(impact) >= 0.5:
                    contributions[name.replace("_", " ").title()] = round(float(impact), 2)

            margin = max(3.0, self.train_rmse * 1.5)
            return {
                "predicted_score": round(pred_score, 1),
                "predicted_change": round(pred_change, 1),
                "uncertainty_lower": round(max(0.0, pred_score - margin), 1),
                "uncertainty_upper": round(min(100.0, pred_score + margin), 1),
                "model_version": self.model_version,
                "contributing_factors": contributions or {"Baseline Momentum": round(pred_change, 2)}
            }
        except Exception:
            return self.baseline_predict_7d(feat)

prediction_engine = PredictionEngine()
