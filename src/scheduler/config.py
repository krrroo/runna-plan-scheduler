from dataclasses import dataclass


@dataclass(frozen=True)
class Rules:
    """Holds limitations for each training plan"""

    weekly_distance_increase: float
    missed_distance_threshold: float
    taper_weeks_decrease: float
    max_quality_sessions_per_week: int


DEFAULT_RULES = Rules(
    weekly_distance_increase=0.1,
    missed_distance_threshold=0.9,
    taper_weeks_decrease=0.2,
    max_quality_sessions_per_week=2,
)


@dataclass(frozen=True)
class GoalProfile:
    """Holds characteristics of training plans designed by coaches"""

    name: str
    distance_km: float
    min_weeks: int
    max_weeks: int
    taper_weeks: int
    peak_weekly_km: float
    peak_long_run_km: float

    def __post_init__(self) -> None:
        if self.taper_weeks >= self.min_weeks:
            raise ValueError("Plan must be longer than taper weeks length.")


PLAN_5K = GoalProfile(
    name="5k",
    distance_km=5.0,
    min_weeks=8,
    max_weeks=12,
    taper_weeks=1,
    peak_weekly_km=25,
    peak_long_run_km=9,
)

PLAN_10K = GoalProfile(
    name="10k",
    distance_km=10.0,
    min_weeks=10,
    max_weeks=14,
    taper_weeks=1,
    peak_weekly_km=30,
    peak_long_run_km=13,
)

PLAN_HALF_MARATHON = GoalProfile(
    name="HalfMarathon",
    distance_km=21.0975,
    min_weeks=12,
    max_weeks=16,
    taper_weeks=2,
    peak_weekly_km=38,
    peak_long_run_km=18,
)
