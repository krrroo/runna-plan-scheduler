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
