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


def weekly_km_targets(
    curve_length: int,
    taper_weeks: int,
    peak_km: float,
    max_increase: float,
    taper_decrease: float,
) -> list[float]:
    """Returns a weekly km target for every week of the curve.

    Weeks build up to peak_km at a value of max_increase per week, peak in the
    week before the taper, then drop by taper_decrease each taper week.
    """

    peak_index = curve_length - taper_weeks - 1
    targets = []

    for week_index in range(curve_length):
        if week_index <= peak_index:
            weeks_until_peak = peak_index - week_index
            km = peak_km / (1 + max_increase) ** weeks_until_peak
        else:
            weeks_into_taper = week_index - peak_index
            km = peak_km * (1 - taper_decrease) ** weeks_into_taper
        targets.append(km)

    return targets


def split_week_km(
    session_types: list[str],
    week_km: float,
    long_run_cap: float,
    session_weights: dict[str, float],
) -> list[float]:
    """Splits a week's km across its sessions, in the same order as session_types."""
    if not session_types:
        return []

    total_weight = sum(session_weights[t] for t in session_types)
    distances = [week_km * session_weights[t] / total_weight for t in session_types]

    leftover = 0.0
    for i, session_type in enumerate(session_types):
        if session_type == "long" and distances[i] > long_run_cap:
            leftover += distances[i] - long_run_cap
            distances[i] = long_run_cap

    other_sessions = [i for i, t in enumerate(session_types) if t != "long"]
    if leftover > 0 and other_sessions:
        share = leftover / len(other_sessions)
        for i in other_sessions:
            distances[i] += share

    distances = [round_to_half(d) for d in distances]  # round every session, every week

    difference = round_to_half(week_km) - sum(distances)
    easy_runs = [i for i, t in enumerate(session_types) if t == "easy"]
    if difference != 0 and easy_runs:
        distances[easy_runs[0]] += difference

    return distances


def progression(curve_length, taper_weeks, start_km, peak_km, taper_decrease) -> list[float]:
    """Returns a weekly km target for every week of the curve.

    Weeks build up to peak_km at a value of step change leading to peak distance based on weeks in in the plan, peak in the
    week before the taper, then drop by taper_decrease each taper week.
    """
    peak_index = curve_length - taper_weeks - 1
    step_change = (peak_km - start_km) / peak_index

    targets = []

    for week_index in range(curve_length):
        if week_index <= peak_index:
            km = start_km + step_change * week_index
        else:
            weeks_into_taper = week_index - peak_index
            km = peak_km * (1 - taper_decrease) ** weeks_into_taper
        targets.append(km)

    return targets
