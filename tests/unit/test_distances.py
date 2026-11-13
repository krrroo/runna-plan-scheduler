import pytest

from scheduler.config import DEFAULT_RULES
from scheduler.distances import round_to_half, split_week_km, weekly_km_targets

WEIGHTS = {"long": 2, "tempo": 1, "intervals": 1, "easy": 1}


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


def test_split_caps_long_run_and_shares_leftover_and_keeps_order():
    # long run capped at 9km should give 1.75 to the rest
    distances = split_week_km(["long", "easy", "tempo"], 25, 9, WEIGHTS)
    assert split_week_km(["tempo", "easy", "long"], 25, 9, WEIGHTS) == [8, 8, 9]
    assert len(distances) == 3
    assert distances[0] == 9


def test_split_with_long_run_under_cap_has_no_leftover():
    # long is under the cap so nothing moves
    assert split_week_km(["easy", "long"], 9, 9, WEIGHTS) == [3, 6]


def test_split_without_long_run_shares_by_weight():
    assert split_week_km(["easy", "tempo"], 10, 9, WEIGHTS) == [5, 5]


def test_split_empty_week_returns_empty_list():
    assert split_week_km([], 10, 9, WEIGHTS) == []


TRAINING_WEEKS = [
    pytest.param(["tempo", "easy", "long"], id="3_sessions"),  # → [10, 10, 18]
    pytest.param(["easy", "tempo", "easy", "long"], id="4_sessions"),  # → [8, 7.5, 7.5, 15]
    pytest.param(
        ["easy", "tempo", "easy", "intervals", "long"], id="5_sessions"
    ),  # → [6, 6.5, 6.5, 6.5, 12.5]
]


@pytest.mark.parametrize("session_types", TRAINING_WEEKS)
def test_split_long_run_is_longest_and_never_exceeds_cap(session_types):
    distances = split_week_km(session_types, 38, 18, WEIGHTS)
    long_run = distances[session_types.index("long")]
    assert long_run <= 18
    assert all(d <= long_run for d in distances)


@pytest.mark.parametrize("session_types", TRAINING_WEEKS)
def test_split_distances_are_multiples_of_half_km(session_types):
    distances = split_week_km(session_types, 38, 18, WEIGHTS)
    assert all(d * 2 == int(d * 2) for d in distances)


def test_split_total_matches_rounded_target():
    # target 23.3; after split 7.15, 7.15, 9; rounded 7, 7, 9 = 23;
    # target rounds to 23.5 (easy gets +0.5)
    distances = split_week_km(["easy", "tempo", "long"], 23.3, 9, WEIGHTS)
    assert distances == [7.5, 7, 9]
    assert sum(distances) == 23.5
