from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from scheduler.generator import monday_of_week_date


@given(st.dates(min_value=date(2020, 1, 1), max_value=date(2040, 12, 31)))
def test_monday_of_week_date_properties(day):
    result = monday_of_week_date(day)

    assert result.weekday() == 0  # day is always Monday
    assert 0 <= (day - result).days <= 6  # day is always within 7 days
    assert day.isocalendar().week == result.isocalendar().week  # days are in the same week
