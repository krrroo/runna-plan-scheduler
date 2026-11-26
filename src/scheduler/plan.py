from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from scheduler.config import GoalProfile

SessionType = Literal["easy", "tempo", "intervals", "long", "race"]


@dataclass(frozen=True)
class Runner:
    """One runners characteristics"""

    runner_id: str
    current_race_distance_km: float
    current_race_time: timedelta
    training_days: tuple[int, ...]  # 0 = Monday … 6 = Sunday
    long_run_day: int  # one of training_days
    time_zone: str

    def __post_init__(self) -> None:
        if len(self.training_days) < 3:
            raise ValueError("Choose at least 3 training days per week.")
        if list(self.training_days) != sorted(set(self.training_days)):
            raise ValueError("Training days must be in weekday order.")
        if self.long_run_day not in self.training_days:
            raise ValueError("Long run day must be one of the training days.")
        if self.current_race_distance_km <= 0:
            raise ValueError("Race distance must be greater than 0 km.")
        if self.current_race_time <= timedelta(0):
            raise ValueError("Race time must be greater than 0.")

        try:
            ZoneInfo(self.time_zone)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"Unknown time zone '{self.time_zone}'.") from None


@dataclass(frozen=True)
class RaceGoal:
    """Runners selected training plan and race date"""

    profile: GoalProfile  # training plan
    race_date: date


@dataclass(frozen=True)
class Session:
    """One planned run"""

    date: date
    session_type: SessionType
    distance_km: float


@dataclass(frozen=True)
class CompletedRun:
    """Tracks runners actual distance per run"""

    runner_id: str
    source_id: str
    date: date
    distance_km: float


@dataclass(frozen=True)
class Week:
    """7 days in a training plan, built from Sessions"""

    start_date: date
    sessions: tuple[Session, ...]

    def total_plan_distance(self) -> float:
        """Returns weeks total distance in kms"""
        return sum(session.distance_km for session in self.sessions)

    def total_actual_distance(self, runs: list[CompletedRun]) -> float:
        """Returns weeks actual distance in kms"""
        week_end = self.start_date + timedelta(days=7)
        return sum(r.distance_km for r in runs if self.start_date <= r.date < week_end)


@dataclass(frozen=True)
class Plan:
    """Full training plan, built with Weeks"""

    weeks: tuple[Week, ...]
