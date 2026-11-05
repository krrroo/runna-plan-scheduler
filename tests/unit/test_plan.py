import pytest
from datetime import date
from scheduler.plan import Session, Week


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