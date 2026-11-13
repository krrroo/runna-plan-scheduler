from dataclasses import replace

import pytest

from scheduler.config import PLAN_5K


@pytest.mark.parametrize("taper_weeks", [1, 2])
def test_profile_fails_when_taper_is_too_long(taper_weeks):
    with pytest.raises(ValueError, match="Plan must be longer than taper"):
        replace(PLAN_5K, min_weeks=1, taper_weeks=taper_weeks)
