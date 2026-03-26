"""Analytics service for rescue operation insights."""

from datetime import datetime, timedelta
from src.models.database import Database


class AnalyticsService:
    """Generate analytics and insights for rescue operations."""

    def __init__(self, db: Database):
        self.db = db

    def response_time_stats(self) -> dict:
        """Calculate average response times."""
        reports = self.db.get_reports()
        times = []
        for r in reports:
            if r.get("status") in ("in_progress", "rescued"):
                created = datetime.fromisoformat(r["created_at"])
                elapsed = (datetime.now() - created).total_seconds() / 60
                times.append(elapsed)

        if not times:
            return {"avg_minutes": 0, "min_minutes": 0, "max_minutes": 0}

        return {
            "avg_minutes": round(sum(times) / len(times), 1),
            "min_minutes": round(min(times), 1),
            "max_minutes": round(max(times), 1),
            "total_operations": len(times),
        }

    def severity_distribution(self) -> dict:
        """Get distribution of reports by severity."""
        reports = self.db.get_reports()
        dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for r in reports:
            sev = r.get("severity", "medium")
            dist[sev] = dist.get(sev, 0) + 1
        return dist

    def team_utilization(self) -> dict:
        """Calculate team utilization rate."""
        teams = self.db.get_teams()
        total = len(teams)
        busy = sum(1 for t in teams if not t.get("is_available", True))
        return {
            "total_teams": total,
            "active": busy,
            "available": total - busy,
            "utilization_pct": round(busy / total * 100, 1) if total > 0 else 0,
        }
