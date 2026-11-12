import pytest

from scheduler.config import DEFAULT_RULES
from scheduler.volume import weekly_km_targets


@pytest.mark.parametrize(
    "curve_length, taper_weeks, peak_weekly_km, manual_calculation",
    [
        (12, 1, 25, 9.64),  # 5k: 25 / 1.1^10
        (16, 2, 38, 11.01),  # half: 38 / 1.1^13
    ],
)
def test_weekly_km_targets_builds_to_peak_then_tapers(
    curve_length, taper_weeks, peak_weekly_km, manual_calculation
):
    rules = DEFAULT_RULES
    full_curve = weekly_km_targets(
        curve_length=curve_length,
        taper_weeks=taper_weeks,
        peak_km=peak_weekly_km,
        max_increase=rules.weekly_distance_increase,
        taper_decrease=rules.taper_weeks_decrease,
    )

    peak_index = curve_length - taper_weeks - 1

    assert len(full_curve) == curve_length  # one target per week
    assert full_curve[peak_index] == pytest.approx(peak_weekly_km)  # peak week value

    for x in range(1, peak_index + 1):  # each build-up week grows by 10%
        assert full_curve[x] == pytest.approx(
            full_curve[x - 1] * (1 + rules.weekly_distance_increase)
        )

    for x in range(peak_index + 1, curve_length):  # each taper week drops by 20%
        assert full_curve[x] == pytest.approx(full_curve[x - 1] * (1 - rules.taper_weeks_decrease))

    assert full_curve[-1] == min(full_curve[peak_index:])  # race week lowest in taper
    assert full_curve[0] == pytest.approx(manual_calculation, rel=0.01)  # hand-checked first week
