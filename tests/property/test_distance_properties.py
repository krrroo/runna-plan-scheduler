from hypothesis import given
from hypothesis import strategies as st

from scheduler.distances import round_to_half


@given(st.floats(min_value=0, max_value=100))
def test_round_to_half_properties(km):
    result = round_to_half(km)

    assert result * 2 == int(result * 2)  # a multiple of 0.5
    assert abs(result - km) <= 0.25  # never more than 0.25 away
