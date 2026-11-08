import pytest
from datetime import date, timedelta
from scheduler.plan import Session, Week, Runner


def test_week_total_distance_sums_its_sessions():
    sessions = (
        Session(date=date(2026, 12, 8), session_type="easy", distance_km=5.0),
        Session(date=date(2026, 12, 10), session_type="tempo", distance_km=6.5),
        Session(date=date(2026, 12, 12), session_type="long", distance_km=8.0),
    )
    week = Week(start_date=date(2026, 12, 7), sessions=sessions)
    
    total = week.total_distance()

    assert total == pytest.approx(19.5)

def test_week_total_distance_returns_0_when_no_sessions():
    week = Week(start_date=date(2026, 12, 7), sessions=())
    
    total = week.total_distance()

    assert total == 0

@pytest.mark.parametrize(
    "training_days, long_run_day, message",
    [
        ((1, 6), 6, "Choose at least 3"),
        ((4, 5, 1), 5, "Training days must be in weekday order"),
        ((1, 3, 3, 6), 6, "Training days must be in weekday order"),
        ((1, 3, 5), 6, "Long run day"),
    ]
)
def test_runner_rejects_invalid_training_days(training_days, long_run_day, message):
    with pytest.raises(ValueError, match=message):
        Runner(
            current_race_time=timedelta(minutes=30, seconds=12),
            current_race_distance_km=5.0,
            training_days=training_days,
            long_run_day=long_run_day,
        )

def test_runner_accepts_valid_training_days():
    runner = Runner(
        current_race_time=timedelta(minutes=30, seconds=12),
        current_race_distance_km=5.0,
        training_days=(1, 3, 6),
        long_run_day=6,
    )
    assert runner.training_days == (1, 3, 6)
