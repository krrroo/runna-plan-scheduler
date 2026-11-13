import itertools

import pytest

from scheduler.config import DEFAULT_RULES, PLAN_5K, PLAN_10K, PLAN_HALF_MARATHON
from scheduler.distances import progression, round_to_half

WEIGHTS = {"long": 2, "tempo": 1, "intervals": 1, "easy": 1}


@pytest.mark.parametrize(
    "float_value, rounded_value",
    [
        (4.74, 4.5),
        (4.76, 5.0),
        (4.25, 4.0),
        (4.0, 4.0),
    ],
)
def test_round_to_half_values_as_expected(float_value, rounded_value):
    assert round_to_half(float_value) == rounded_value


PLANS = [PLAN_5K, PLAN_10K, PLAN_HALF_MARATHON]
SESSION_TYPES = ["long_run", "easy", "tempo", "intervals"]

CURVE_CASES = [
    pytest.param(plan, session_type, id=f"{plan.name}-{session_type}")
    for plan in PLANS
    for session_type in SESSION_TYPES
]


@pytest.mark.parametrize("plan, session_type", CURVE_CASES)
def test__builds_correctly(plan, session_type):
    start_km = getattr(plan, f"{session_type}_start_km")
    peak_km = getattr(plan, f"{session_type}_peak_km")
    peak_index = plan.max_weeks - plan.taper_weeks - 1

    targets = progression(
        curve_length=plan.max_weeks,
        taper_weeks=plan.taper_weeks,
        start_km=start_km,
        peak_km=peak_km,
        taper_decrease=DEFAULT_RULES.taper_weeks_decrease,
    )

    # plan has the right length
    assert len(targets) == plan.max_weeks
    # starts on the right km
    assert targets[0] == pytest.approx(start_km)
    # peak is at the right index
    assert targets[peak_index] == pytest.approx(peak_km)

    # the steps up are all equal
    build_up = targets[: peak_index + 1]
    steps = [later - earlier for earlier, later in itertools.pairwise(build_up)]
    assert all(step == pytest.approx(steps[0]) for step in steps)

    # the taper decreases by taper_decrease each week
    taper = targets[peak_index:]
    for earlier, later in itertools.pairwise(taper):
        assert later == pytest.approx(earlier * (1 - DEFAULT_RULES.taper_weeks_decrease))
        assert later < earlier
