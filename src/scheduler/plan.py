from dataclasses import dataclass
from datetime import timedelta, date
from typing import Literal

from scheduler.config import GoalProfile

SessionType = Literal["easy", "tempo", "intervals", "long"]

@dataclass(frozen=True)
class Runner:
    """One runners characteristics"""
    current_race_distance_km: float
    current_race_time: timedelta
    training_days: tuple[int, ...]      # 0 = Monday … 6 = Sunday
    long_run_day: int                   # one of training_days

@dataclass(frozen=True)
class RaceGoal:
    """Runners selected training plan and race date"""
    profile: GoalProfile                # training plan
    race_date: date

@dataclass(frozen=True)
class Session:
    """One planned run"""
    date: date
    session_type: SessionType
    distance_km: float

@dataclass(frozen=True)
class Week:
    """7 days in a training plan, built from Sessions"""
    start_date: date
    sessions: tuple[Session, ...]

    def total_distance(self) -> float:
        """Returns weeks total distance in kms"""
        return sum(session.distance_km for session in self.sessions)

@dataclass(frozen=True)
class Plan:
    """Full training plan, built with Weeks"""
    weeks: tuple[Week, ...]
