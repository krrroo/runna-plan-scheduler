import pytest
from datetime import date, timedelta
from scheduler.generator import monday_of_week_date, weeks_in_plan, PlanGenerator
from scheduler.plan import Runner, RaceGoal, Plan
from scheduler.config import PLAN_5K, DEFAULT_RULES

RACE_DATE = date(2027, 3, 7)

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

