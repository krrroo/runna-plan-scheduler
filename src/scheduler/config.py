from dataclasses import dataclass


@dataclass(frozen=True)
class Rules:
    """Holds limitations for each training plan"""

    weekly_distance_increase: float
    missed_distance_threshold: float
    taper_weeks_decrease: float
    max_quality_sessions_per_week: int
    min_session_km: float
    session_weights: dict[str, float]


DEFAULT_RULES = Rules(
    weekly_distance_increase=0.1,
    missed_distance_threshold=0.9,
    taper_weeks_decrease=0.2,
    max_quality_sessions_per_week=2,
    min_session_km=3.5,
    session_weights={"long": 2, "tempo": 1, "intervals": 1, "easy": 1},
)


@dataclass(frozen=True)
class GoalProfile:
    """Holds characteristics of training plans designed by coaches"""

    name: str
    distance_km: float
    min_weeks: int
    max_weeks: int
    taper_weeks: int
    long_run_start_km: float
    long_run_peak_km: float
    easy_start_km: float
    easy_peak_km: float
    tempo_start_km: float
    tempo_peak_km: float
    intervals_start_km: float
    intervals_peak_km: float
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
    long_run_start_km=5.0,
    long_run_peak_km=8.0,
    easy_start_km=3.5,
    easy_peak_km=5.0,
    tempo_start_km=3.5,
    tempo_peak_km=4.5,
    intervals_start_km=3.5,
    intervals_peak_km=4.0,
    peak_weekly_km=25.0,
    peak_long_run_km=9.0,
)

PLAN_10K = GoalProfile(
    name="10k",
    distance_km=10.0,
    min_weeks=10,
    max_weeks=14,
    taper_weeks=1,
    long_run_start_km=6.0,
    long_run_peak_km=12.0,
    easy_start_km=4.0,
    easy_peak_km=6.0,
    tempo_start_km=4.0,
    tempo_peak_km=5.5,
    intervals_start_km=3.5,
    intervals_peak_km=5.0,
    peak_weekly_km=30.0,
    peak_long_run_km=13.0,
)

PLAN_HALF_MARATHON = GoalProfile(
    name="HalfMarathon",
    distance_km=21.0975,
    min_weeks=12,
    max_weeks=16,
    taper_weeks=2,
    long_run_start_km=6.0,
    long_run_peak_km=18.0,
    easy_start_km=4.5,
    easy_peak_km=7.0,
    tempo_start_km=4.5,
    tempo_peak_km=6.5,
    intervals_start_km=4.0,
    intervals_peak_km=6.0,
    peak_weekly_km=38.0,
    peak_long_run_km=18.0,
)
