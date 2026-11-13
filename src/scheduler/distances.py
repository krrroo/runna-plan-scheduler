from dataclasses import dataclass


@dataclass(frozen=True)
class WeekDistances:
    long_km: float
    easy_km: float
    tempo_km: float
    intervals_km: float


def round_to_half(km: float) -> float:
    """Rounds a distance to the nearest 0.5 km."""
    return round(km * 2) / 2


def progression(curve_length, taper_weeks, start_km, peak_km, taper_decrease) -> list[float]:
    """Returns a weekly km target for every week of the curve.

    Weeks build up to peak_km at a value of step change leading to peak distance based on weeks in in the plan, peak in the
    week before the taper, then drop by taper_decrease each taper week.
    """
    peak_index = curve_length - taper_weeks - 1
    step_change = (peak_km - start_km) / peak_index if peak_index > 0 else 0.0

    targets = []

    for week_index in range(curve_length):
        if week_index <= peak_index:
            km = start_km + step_change * week_index
        else:
            weeks_into_taper = week_index - peak_index
            km = peak_km * (1 - taper_decrease) ** weeks_into_taper
        targets.append(km)

    return targets
