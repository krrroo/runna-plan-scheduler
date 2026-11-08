import pytest
from datetime import date, timedelta
from scheduler.generator import monday_of_week_date, weeks_in_plan, PlanGenerator
from scheduler.plan import Runner, RaceGoal, Plan
from scheduler.config import PLAN_5K, DEFAULT_RULES

RACE_DATE = date(2027, 3, 7)
HARD_SESSIONS = {"tempo", "intervals", "long", "race"}
QUALITY_SESSIONS = {"tempo", "intervals"}


def all_sessions(plan):
    return [s for week in plan.weeks for s in week.sessions]

def make_plan(generator, training_days, long_run_day, start_date=date(2026,12,14), race_date=RACE_DATE):
    runner = Runner(
        current_race_time=timedelta(minutes=30, seconds=12),
        current_race_distance_km=5.0,
        training_days=training_days,
        long_run_day=long_run_day,
    )
    goal = RaceGoal(race_date=race_date, profile=PLAN_5K)
    return generator.generate_training_plan(runner=runner, goal=goal, start_date=start_date)

@pytest.fixture(params=[6, 5], ids=["sunday_long_run", "saturday_long_run"])
def runner(request):
    return Runner(
        current_race_time=timedelta(minutes=30, seconds=12),
        current_race_distance_km=5.0,
        training_days=(1, 3, 4, 5, 6),
        long_run_day=request.param,
    )

@pytest.fixture
def generator():
    return PlanGenerator(
        rules=DEFAULT_RULES
    )

@pytest.fixture
def base_plan(runner, generator):
    goal = RaceGoal(race_date=date(2027, 3, 7), profile=PLAN_5K)
    return generator.generate_training_plan(runner=runner, goal=goal, start_date=date(2026, 12, 14))


@pytest.mark.parametrize(
    "d, expected",
    [
        (date(2026,11,6), date(2026,11,2)), # Friday returns earlier Monday
        (date(2026,11,2), date(2026,11,2)), # Monday returns itself
        (date(2026,11,8), date(2026,11,2)), # Sunday returns earlier Monday

    ],
)
def test_monday_of_week_returns_monday(d, expected):
    assert monday_of_week_date(d) == expected

def test_weeks_in_plan_returns_correct_number():
    start_date = date(2026,11,2)
    end_date = date(2026,11,16)
    assert weeks_in_plan(start_date, end_date) == 3

@pytest.mark.parametrize(
    "training_start_date, race_date, expected_start_date, expected_race_date, expected_plan_length",
    [
        (date(2026,12,16), date(2027,3,7), date(2026,12,14), date(2027,3,1), 12),   # exact plan length
        (date(2026,12,2), date(2027,3,7), date(2026,12,14), date(2027,3,1), 12),    # longer than max plan weeks
        (date(2026,12,30), date(2027,3,7), date(2026,12,28), date(2027,3,1), 10),   # between max and min plan weeks
        (date(2027,1,24), date(2027,3,7), date(2027,1,18), date(2027,3,1), 7),   # below min plan weeks
        
    ]
)
def test_plan_succeeds_and_generates_exact_number_of_weeks(runner, generator, training_start_date, race_date, expected_start_date, expected_race_date, expected_plan_length):
    race_goal = RaceGoal(race_date=race_date, profile=PLAN_5K)
    generated_plan = generator.generate_training_plan(runner=runner,goal=race_goal,start_date=training_start_date)
    
    assert isinstance(generated_plan, Plan)
    assert generated_plan.weeks[0].start_date == expected_start_date
    assert generated_plan.weeks[-1].start_date == expected_race_date
    assert len(generated_plan.weeks) == expected_plan_length

def test_plan_fails_when_time_shorter_than_half_min_weeks(runner, generator):
    training_start_date = date(2027,2,14)
    race_date = date(2027,3,7)
    race_goal = RaceGoal(race_date=race_date, profile=PLAN_5K)
    
    with pytest.raises(ValueError, match="Your race is too soon"):
        generator.generate_training_plan(runner=runner,goal=race_goal,start_date=training_start_date)

def sessions_of_type(week, session_type):
    return [s for s in week.sessions if s.session_type == session_type]

def test_every_non_race_week_has_one_long_run_on_long_run_day(base_plan, runner):
    for week in base_plan.weeks[:-1]:
        long_runs = sessions_of_type(week, "long")
        assert len(long_runs) == 1
        assert long_runs[0].date.weekday() == runner.long_run_day

def test_race_week_has_no_long_run(base_plan):
    assert sessions_of_type(base_plan.weeks[-1], "long") == []

def test_plan_has_one_race_in_last_week(base_plan):
    races = [s for week in base_plan.weeks for s in week.sessions if s.session_type == "race"]
    assert len(races) == 1
    assert races[0] in base_plan.weeks[-1].sessions
    assert races[0].date == RACE_DATE
    assert races[0].distance_km == PLAN_5K.distance_km

def test_no_sessions_after_race(base_plan):
    for week in base_plan.weeks:
        for session in week.sessions:
            if session.session_type != "race":
                assert session.date < RACE_DATE

def test_no_long_run_in_week_one_when_start_is_after_long_run_day(generator):
    plan = make_plan(generator, training_days=(1, 3, 6), long_run_day=1, start_date=date(2026, 12, 16))
    assert sessions_of_type(plan.weeks[0], "long") == []
    assert len(sessions_of_type(plan.weeks[1], "long")) == 1

def test_race_on_non_training_day_still_scheduled(generator):
    race_date = date(2027, 3, 6)
    plan = make_plan(generator, training_days=(1, 3, 6), long_run_day=6, race_date=race_date)
    races = [s for s in all_sessions(plan) if s.session_type == "race"]
    assert len(races) == 1
    assert races[0].date == race_date

def test_no_sessions_before_start_date(generator):
    start_date = date(2026, 12, 16)
    plan = make_plan(generator, training_days=(1, 3, 5, 6), long_run_day=6, start_date=start_date)
    for session in all_sessions(plan):
        assert session.date >= start_date

def test_day_after_long_run_is_easy(generator):
    plan = make_plan(generator, training_days=(0, 3, 6), long_run_day=6)
    mondays = [s for s in all_sessions(plan) if s.date.weekday() == 0]
    assert mondays
    for session in mondays:
        assert session.session_type == "easy"

def test_day_before_long_run_is_easy(base_plan, runner):
    day_before = (runner.long_run_day - 1) % 7
    sessions = [s for s in all_sessions(base_plan) if s.date.weekday() == day_before]
    assert sessions
    for session in sessions:
        assert session.session_type == "easy"

def test_day_before_race_is_easy(base_plan):
    day_before = [s for s in all_sessions(base_plan) if s.date == RACE_DATE - timedelta(days=1)]
    assert len(day_before) == 1
    assert day_before[0].session_type == "easy"

def test_no_two_hard_sessions_on_consecutive_days(base_plan):
    sessions = sorted(all_sessions(base_plan), key=lambda s: s.date)
    for earlier, later in zip(sessions, sessions[1:]):
        if later.date - earlier.date == timedelta(days=1):
            assert not (earlier.session_type in HARD_SESSIONS and later.session_type in HARD_SESSIONS)

@pytest.mark.parametrize(
    "training_days, expected_quality_max",
    [
        ((1, 3, 6), 1),            # 3 days have 1 quality session
        ((1, 2, 3, 5, 6), 2),      # any more than 3 are capped at 2 quality sessions
    ]
)
def test_quality_sessions_capped_per_week(generator, training_days, expected_quality_max):
    plan = make_plan(generator, training_days=training_days, long_run_day=6)
    for week in plan.weeks:
        quality = [s for s in week.sessions if s.session_type in QUALITY_SESSIONS]
        assert len(quality) <= expected_quality_max

def test_quality_allowed_with_rest_day_before_long_run(generator):
    # Mon, Fri, Sun; Sun long run; Fri can be quality bc Sat is rest
    plan = make_plan(generator, training_days=(0, 4, 6), long_run_day=6)
    fridays = [s for s in all_sessions(plan) if s.date.weekday() == 4]
    assert fridays
    for session in fridays:
        assert session.session_type in QUALITY_SESSIONS

def test_no_quality_when_training_days_are_bunched(generator):
    # quality session is skipped if runner trains only 3 day and they're all back to back 
    plan = make_plan(generator, training_days=(0, 5, 6), long_run_day=6)
    quality = [s for s in all_sessions(plan) if s.session_type in QUALITY_SESSIONS]
    assert quality == []

def test_three_day_runner_gets_both_tempo_and_intervals(generator):
    plan = make_plan(generator, training_days=(1, 3, 6), long_run_day=6)
    types = {s.session_type for s in all_sessions(plan)}
    assert "tempo" in types
    assert "intervals" in types


