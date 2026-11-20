from dataclasses import dataclass, replace
from datetime import date, timedelta

from scheduler.config import DEFAULT_RULES, Rules
from scheduler.distances import WeekDistances, progression, round_to_half
from scheduler.plan import CompletedRun, Plan, RaceGoal, Runner, Week
from scheduler.session_rules import build_week_sessions


def monday_of_week_date(d: date) -> date:
    """Returns the Monday of the week containing the given date."""
    return d - timedelta(days=d.weekday())


def weeks_in_plan(start_date: date, end_date: date) -> int:
    """Counts weeks from the start Monday to the end Monday, inclusive."""
    return (end_date - start_date).days // 7 + 1


@dataclass
class PlanGenerator:
    rules: Rules = DEFAULT_RULES

    def generate_training_plan(self, runner: Runner, goal: RaceGoal, start_date: date) -> Plan:
        """Builds a training plan from the coaches' design, applying the plan rules."""
        race_date_monday = monday_of_week_date(goal.race_date)
        plan_start_week_monday = monday_of_week_date(start_date)
        plan_weeks = weeks_in_plan(plan_start_week_monday, race_date_monday)
        max_plan_weeks = goal.profile.max_weeks
        min_plan_weeks = goal.profile.min_weeks
        max_quality = min(self.rules.max_quality_sessions_per_week, len(runner.training_days) - 2)

        if plan_weeks <= min_plan_weeks / 2:
            raise ValueError(
                "Your race is too soon to train for safely. Please choose a different race goal."
            )
        elif plan_weeks > max_plan_weeks:
            plan_max_diff = plan_weeks - max_plan_weeks
            plan_start_date = plan_start_week_monday + timedelta(weeks=plan_max_diff)
        else:
            plan_start_date = plan_start_week_monday

        # One progression curve per session type. Runners with fewer than min_weeks
        # get the last part of a min_weeks-long curve, as if they had started earlier.
        profile = goal.profile
        actual_weeks = min(plan_weeks, max_plan_weeks)
        curve_length = max(actual_weeks, min_plan_weeks)
        taper_decrease = self.rules.taper_weeks_decrease

        # TODO: simplify this design to have one call
        long_curve = progression(
            curve_length=curve_length,
            taper_weeks=profile.taper_weeks,
            start_km=profile.long_run_start_km,
            peak_km=profile.long_run_peak_km,
            taper_decrease=taper_decrease,
        )[-actual_weeks:]
        easy_curve = progression(
            curve_length=curve_length,
            taper_weeks=profile.taper_weeks,
            start_km=profile.easy_start_km,
            peak_km=profile.easy_peak_km,
            taper_decrease=taper_decrease,
        )[-actual_weeks:]
        tempo_curve = progression(
            curve_length=curve_length,
            taper_weeks=profile.taper_weeks,
            start_km=profile.tempo_start_km,
            peak_km=profile.tempo_peak_km,
            taper_decrease=taper_decrease,
        )[-actual_weeks:]
        intervals_curve = progression(
            curve_length=curve_length,
            taper_weeks=profile.taper_weeks,
            start_km=profile.intervals_start_km,
            peak_km=profile.intervals_peak_km,
            taper_decrease=taper_decrease,
        )[-actual_weeks:]

        week_start = plan_start_date
        weeks = []
        week_index = 0
        last_hard_date = None

        while week_start <= race_date_monday:
            distances = WeekDistances(
                long_km=long_curve[week_index],
                easy_km=easy_curve[week_index],
                tempo_km=tempo_curve[week_index],
                intervals_km=intervals_curve[week_index],
            )
            sessions, last_hard_date = build_week_sessions(
                week_start=week_start,
                week_index=week_index,
                race_date_monday=race_date_monday,
                start_date=start_date,
                runner=runner,
                goal=goal,
                max_quality=max_quality,
                last_hard_date=last_hard_date,
                distances=distances,
            )
            weeks.append(Week(start_date=week_start, sessions=sessions))
            week_start += timedelta(weeks=1)
            week_index += 1

        return Plan(weeks=tuple(weeks))

    def is_shortfall(self, week: Week, runs: list[CompletedRun]) -> bool:
        """Checks if runner is behind distance threshold."""
        planned = week.total_plan_distance()
        if planned == 0:
            return False
        return week.total_actual_distance(runs) / planned < self.rules.missed_distance_threshold

    def adapt_training_plan(self, plan: Plan, week_index: int, runs: list[CompletedRun]) -> Plan:
        """Adapts training plan from a given week onwards, based on missed distance ratio or max adapt decrease."""
        current_week = plan.weeks[week_index]
        ratio = current_week.total_actual_distance(runs) / current_week.total_plan_distance()

        if ratio >= self.rules.missed_distance_threshold:
            raise ValueError("Adaptation is only for distance shortfall")

        ratio = max(1 - self.rules.max_adapt_decrease, ratio)

        adapted_weeks = []
        for week in plan.weeks[week_index + 1 :]:
            training_km = sum(s.distance_km for s in week.sessions if s.session_type != "race")
            long_km = sum(s.distance_km for s in week.sessions if s.session_type == "long")
            flexible_km = training_km - long_km

            if flexible_km > 0:
                scale = (training_km * ratio - long_km) / flexible_km
                scale = max(self.rules.min_adapt_session_scale, scale)
            else:
                scale = 1.0

            new_sessions = []
            for session in week.sessions:
                if session.session_type in {"long", "race"}:
                    new_sessions.append(session)
                else:
                    new_sessions.append(
                        replace(session, distance_km=round_to_half(session.distance_km * scale))
                    )

            adapted_weeks.append(replace(week, sessions=tuple(new_sessions)))

        return replace(plan, weeks=plan.weeks[: week_index + 1] + tuple(adapted_weeks))
