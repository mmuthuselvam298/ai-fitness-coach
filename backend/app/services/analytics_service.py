"""Analytics service for workout aggregation and progress trends."""

from typing import Any

from app.models.database import db


class AnalyticsService:
    @staticmethod
    def get_progress_overview() -> dict[str, Any]:
        """Aggregate stats, distribution, and temporal performance."""
        data = db.get_analytics()
        overview = data["overview"]

        # If zero sessions yet, provide clean empty baseline
        return {
            "total_workouts": int(overview.get("total_workouts") or 0),
            "total_reps": int(overview.get("total_reps") or 0),
            "avg_form_score": round(float(overview.get("avg_form_score") or 0), 1),
            "best_form_score": round(float(overview.get("best_form_score") or 0), 1),
            "total_duration_minutes": round(float(overview.get("total_duration_seconds") or 0) / 60.0, 1),
            "exercise_distribution": data["exercise_distribution"],
            "recent_trend": data["history_trend"],
        }


analytics_service = AnalyticsService()
