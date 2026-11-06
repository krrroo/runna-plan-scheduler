import pytest
from datetime import date, timedelta
from scheduler.generator import monday_of_week_date, weeks_in_plan, PlanGenerator
from scheduler.plan import Runner, RaceGoal, Plan
from scheduler.config import PLAN_5K, DEFAULT_RULES

@pytest.fixture
def runner():
    return Runner(
        current_race_time=timedelta(minutes=30, seconds=12),
        current_race_distance_km=5.0,
        training_days=(0,1,6),
        long_run_day=6
    )

@pytest.fixture
def generator():
    return PlanGenerator(
        rules=DEFAULT_RULES
    )

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
    #training_start_date = date(2026,12,16)
    #race_date = date(2027,3,7)
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
