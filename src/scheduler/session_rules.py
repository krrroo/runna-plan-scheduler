from datetime import date, timedelta

from scheduler.distances import WeekDistances, round_to_half
from scheduler.plan import RaceGoal, Runner, Session


def is_day_after(day1: int, day2: int) -> bool:
    """Checks if one day of the week is directly after another."""
    return day1 == (day2 + 1) % 7


def build_week_sessions(
    week_start: date,
    week_index: int,
    race_date_monday: date,
    start_date: date,
    runner: Runner,
    goal: RaceGoal,
    max_quality: int,
    last_hard_date: date | None,
    distances: WeekDistances,
) -> tuple[tuple[Session, ...], date | None]:
    """Builds one week's sessions and returns them with the updated last hard session date."""
    sessions = []
    quality_count = 0
    is_race_week = week_start == race_date_monday
    km_by_type = {
        "long": distances.long_km,
        "tempo": distances.tempo_km,
        "intervals": distances.intervals_km,
        "easy": distances.easy_km,
    }

    for day in runner.training_days:
        session_date = week_start + timedelta(days=day)

        if session_date < start_date or session_date >= goal.race_date:
            continue  # skips sessions before start date and after race date
        elif is_race_week and day == runner.long_run_day:
            session_type = "easy"  # long session becomes easy in race week
        elif is_day_after(day, runner.long_run_day) or is_day_after(runner.long_run_day, day):
            session_type = "easy"  # session before or after a long run must be easy
        elif day == runner.long_run_day:
            session_type = "long"  # runner's chosen long run day
            last_hard_date = session_date
        elif is_race_week and is_day_after(goal.race_date.weekday(), day):
            session_type = "easy"  # session before race must be easy
        elif quality_count < max_quality and last_hard_date != session_date - timedelta(days=1):
            session_type = "tempo" if (week_index + quality_count) % 2 == 0 else "intervals"
            quality_count += 1
            last_hard_date = session_date
        else:
            session_type = "easy"

        sessions.append(
            Session(
                date=session_date,
                session_type=session_type,
                distance_km=round_to_half(km_by_type[session_type]),
            )
        )

    if is_race_week:
        sessions.append(
            Session(
                date=goal.race_date,
                session_type="race",
                distance_km=goal.profile.distance_km,
            )
        )

    return tuple(sessions), last_hard_date
