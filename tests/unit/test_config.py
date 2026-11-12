import pytest

from scheduler.config import GoalProfile


@pytest.mark.parametrize("taper_weeks", [(1), (2)])
def test_profile_fails_when_taper_is_too_long(taper_weeks):
    with pytest.raises(ValueError, match="Plan must be longer than taper"):
        GoalProfile(
            name="TEST 5k",
            distance_km=5.0,
            min_weeks=1,
            max_weeks=12,
            taper_weeks=taper_weeks,
            peak_weekly_km=25,
            peak_long_run_km=9,
        )
