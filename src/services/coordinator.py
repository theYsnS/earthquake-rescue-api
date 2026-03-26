import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.models.database import (
    TeamDB, RescueReportDB, haversine_distance,
    get_teams, assign_team
)
from src.models.schemas import Severity, Status, TeamStatus
from src.services.notification import notification_service

logger = logging.getLogger(__name__)

SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 4.0,
    Severity.HIGH: 3.0,
    Severity.MEDIUM: 2.0,
    Severity.LOW: 1.0,
}


class CoordinatorService:
    """Coordinates rescue operations: auto-assignment, priority scoring, resource optimization."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_priority_score(self, report: RescueReportDB) -> float:
        """Calculate priority score = severity_weight * time_elapsed_hours * victim_count."""
        severity_weight = SEVERITY_WEIGHTS.get(report.severity, 1.0)
        elapsed_hours = max(
            (datetime.utcnow() - report.created_at).total_seconds() / 3600.0,
            0.1,  # minimum 0.1 hours to avoid zero scores
        )
        victim_factor = max(report.estimated_victims, 1)
        return severity_weight * elapsed_hours * victim_factor

    def find_nearest_available_team(
        self, latitude: float, longitude: float
    ) -> Optional[TeamDB]:
        """Find the nearest available team to a given location."""
        teams = get_teams(self.db)
        available_teams = [t for t in teams if t.status == TeamStatus.AVAILABLE]

        if not available_teams:
            return None

        nearest_team = None
        min_distance = float("inf")

        for team in available_teams:
            dist = haversine_distance(
                latitude, longitude, team.latitude, team.longitude
            )
            if dist < min_distance:
                min_distance = dist
                nearest_team = team

        return nearest_team

    def try_auto_assign(self, report: RescueReportDB) -> bool:
        """Attempt to automatically assign the nearest available team to a report."""
        # Only auto-assign critical and high severity
        if report.severity not in (Severity.CRITICAL, Severity.HIGH):
            notification_service.notify_new_report(report)
            return False

        nearest_team = self.find_nearest_available_team(
            report.latitude, report.longitude
        )

        if nearest_team:
            assign_team(self.db, nearest_team.id, report.id)
            notification_service.notify_team_assigned(nearest_team, report)
            logger.info(
                f"Auto-assigned team '{nearest_team.name}' (id={nearest_team.id}) "
                f"to report id={report.id}"
            )
            return True
        else:
            notification_service.notify_new_report(report)
            logger.warning(
                f"No available teams for auto-assignment to report id={report.id}"
            )
            return False

    def recalculate_all_priorities(self) -> int:
        """Recalculate priority scores for all pending/in-progress reports."""
        reports = (
            self.db.query(RescueReportDB)
            .filter(RescueReportDB.status.in_([Status.PENDING, Status.IN_PROGRESS]))
            .all()
        )
        count = 0
        for report in reports:
            new_score = self.calculate_priority_score(report)
            report.priority_score = new_score
            count += 1
        self.db.commit()
        logger.info(f"Recalculated priorities for {count} reports")
        return count

    def optimize_assignments(self) -> int:
        """Re-optimize team assignments for pending reports by assigning nearest available teams."""
        pending_reports = (
            self.db.query(RescueReportDB)
            .filter(
                RescueReportDB.status == Status.PENDING,
                RescueReportDB.assigned_team_id.is_(None),
            )
            .order_by(RescueReportDB.priority_score.desc())
            .all()
        )

        assigned_count = 0
        for report in pending_reports:
            nearest_team = self.find_nearest_available_team(
                report.latitude, report.longitude
            )
            if nearest_team:
                assign_team(self.db, nearest_team.id, report.id)
                notification_service.notify_team_assigned(nearest_team, report)
                assigned_count += 1
                logger.info(
                    f"Optimized: assigned team '{nearest_team.name}' to report id={report.id}"
                )
            else:
                break  # No more available teams

        return assigned_count
