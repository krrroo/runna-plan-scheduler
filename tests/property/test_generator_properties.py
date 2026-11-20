import itertools
from datetime import date, timedelta

from hypothesis import given
from hypothesis import strategies as st

from scheduler.config import PLAN_5K, PLAN_10K, PLAN_HALF_MARATHON
from scheduler.generator import PlanGenerator, monday_of_week_date
from scheduler.plan import RaceGoal, Runner

HARD_SESSIONS = {"tempo", "intervals", "long", "race"}


def all_sessions(plan):
    return [s for week in plan.weeks for s in week.sessions]


def build_plan(runner, inputs):
    goal, start_date = inputs
    return PlanGenerator().generate_training_plan(runner, goal, start_date)


@given(st.dates(min_value=date(2020, 1, 1), max_value=date(2040, 12, 31)))
def test_monday_of_week_date_properties(day):
    result = monday_of_week_date(day)

    assert result.weekday() == 0  # day is always Monday
    assert 0 <= (day - result).days <= 6  # day is always within 7 days
    assert day.isocalendar().week == result.isocalendar().week  # days are in the same week


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


@given(runners(), plan_inputs())
def test_builds_plan_for_any_valid_input(runner, inputs):
    plan = build_plan(runner, inputs)
    assert len(plan.weeks) > 0


@given(runners(), plan_inputs())
def test_no_back_to_back_hard_sessions(runner, inputs):
    plan = build_plan(runner, inputs)
    sessions = all_sessions(plan)
    for earlier, later in itertools.pairwise(sessions):
        if later.date - earlier.date == timedelta(days=1):
            assert not (
                earlier.session_type in HARD_SESSIONS and later.session_type in HARD_SESSIONS
            ), f"Hard sessions back to back: {earlier} then {later}"
