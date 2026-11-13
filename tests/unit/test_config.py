from dataclasses import replace

import pytest

from scheduler.config import DEFAULT_RULES, PLAN_5K, PLAN_10K, PLAN_HALF_MARATHON


@pytest.mark.parametrize("taper_weeks", [1, 2])
def test_profile_fails_when_taper_is_too_long(taper_weeks):
    with pytest.raises(ValueError, match="Plan must be longer than taper"):
        replace(PLAN_5K, min_weeks=1, taper_weeks=taper_weeks)


@pytest.mark.parametrize("plan", [PLAN_5K, PLAN_10K, PLAN_HALF_MARATHON], ids=lambda p: p.name)
def test_profile_start_distances_meet_minimum(plan):
    for session_type in ["long_run", "easy", "tempo", "intervals"]:
        assert getattr(plan, f"{session_type}_start_km") >= DEFAULT_RULES.min_session_km
