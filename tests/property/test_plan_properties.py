from datetime import timedelta, date

from hypothesis import given
from hypothesis import strategies as st

from scheduler.plan import Runner
from scheduler.config import PLAN_5K, PLAN_10K, PLAN_HALF_MARATHON
from scheduler.generator import monday_of_week_date


@st.composite
def runners(draw):
    days = draw(
        st.lists(st.integers(min_value=0, max_value=6), min_size=3, max_size=6, unique=True)
    )
    training_days = tuple(sorted(days))
    long_run_day = draw(st.sampled_from(training_days))
    return Runner(
        current_race_time=timedelta(minutes=30),
        current_race_distance_km=5.0,
        training_days=training_days,
        long_run_day=long_run_day,
    )


@given(runners())
def test_runner_long_run_day_is_a_training_day(runner):
    assert runner.long_run_day in runner.training_days

@st.composite
def plan_inputs(draw):
    start_date = draw(st.dates(min_value=date(2020, 1, 1), max_value=date(2040, 12, 31)))
    profile = draw(st.sampled_from([PLAN_5K, PLAN_10K, PLAN_HALF_MARATHON]))
    weeks_to_race = draw(
        st.integers(min_value=profile.min_weeks // 2 + 1, max_value=profile.max_weeks + 3)
    )
    day_in_race_week = draw(st.integers(min_value=0, max_value=6))

    race_date = (
        monday_of_week_date(start_date)
        + timedelta(weeks=weeks_to_race - 1)
        + timedelta(days=day_in_race_week)
    )
    goal = RaceGoal(profile=profile, race_date=race_date)
    return goal, start_date