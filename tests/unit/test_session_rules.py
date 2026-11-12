from datetime import date, timedelta

import pytest

from scheduler.config import DEFAULT_RULES, PLAN_5K
from scheduler.plan import RaceGoal, Runner
from scheduler.session_rules import build_week_sessions, is_day_after

RACE_DATE = date(2027, 3, 7)  # Sunday
RACE_WEEK_MONDAY = date(2027, 3, 1)
PLAN_START = date(2026, 12, 14)  # Monday
GOAL = RaceGoal(race_date=RACE_DATE, profile=PLAN_5K)


def make_runner(training_days=(1, 3, 6), long_run_day=6):
    return Runner(
        current_race_time=timedelta(minutes=30, seconds=12),
        current_race_distance_km=5.0,
        training_days=training_days,
        long_run_day=long_run_day,
    )


def build(week_start=PLAN_START, week_index=0, start_date=PLAN_START, last_hard_date=None):
    return build_week_sessions(
        week_start=week_start,
        week_index=week_index,
        race_date_monday=RACE_WEEK_MONDAY,
        start_date=start_date,
        runner=make_runner(),
        goal=GOAL,
        max_quality=1,
        last_hard_date=last_hard_date,
        week_km=0.0,
        session_weights=DEFAULT_RULES.session_weights,
    )


def types_of(sessions):
    return [s.session_type for s in sessions]


@pytest.mark.parametrize(
    "day, other_day, expected",
    [
        (0, 6, True),  # Monday is after Sunday (wraps around)
        (3, 2, True),  # Thursday is after Wednesday
        (1, 6, False),  # Tuesday is not after Sunday
        (6, 6, False),  # same day
    ],
)
def test_is_day_after(day, other_day, expected):
    assert is_day_after(day, other_day) == expected


def test_normal_week_gets_quality_easy_and_long():
    # Tue, Thu, Sun with a Sunday long run; max 1 quality
    sessions, last_hard_date = build()
    assert types_of(sessions) == ["tempo", "easy", "long"]
    assert last_hard_date == date(2026, 12, 20)  # the Sunday long run


def test_odd_week_index_gives_intervals():
    sessions, _ = build(week_index=1)
    assert types_of(sessions)[0] == "intervals"


def test_hard_day_from_previous_week_blocks_quality_next_day():
    # Monday 14 Dec was hard, so Tuesday can't be quality and Thursday gets it instead
    sessions, _ = build(last_hard_date=date(2026, 12, 14))
    assert types_of(sessions) == ["easy", "tempo", "long"]


def test_days_before_start_date_are_skipped():
    # starting Wednesday 16 Dec, so Tuesday 15 Dec is dropped
    sessions, _ = build(start_date=date(2026, 12, 16))
    assert [s.date for s in sessions] == [date(2026, 12, 17), date(2026, 12, 20)]
    assert types_of(sessions) == ["tempo", "long"]


def test_race_week_ends_with_race_and_no_long_run():
    sessions, _ = build(week_start=RACE_WEEK_MONDAY)
    assert types_of(sessions) == ["tempo", "easy", "race"]
    assert sessions[-1].date == RACE_DATE
    assert sessions[-1].distance_km == PLAN_5K.distance_km


def test_returns_tuple_of_sessions():
    sessions, _ = build()
    assert isinstance(sessions, tuple)
