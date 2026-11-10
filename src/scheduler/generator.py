from dataclasses import dataclass
from datetime import date, timedelta

from scheduler.config import DEFAULT_RULES, Rules
from scheduler.plan import Plan, RaceGoal, Runner, Session, Week


def monday_of_week_date(d: date) -> date:
    """Returns a Monday of a week from a given date"""
    return d - timedelta(days=d.weekday())


def weeks_in_plan(start_date: date, end_date: date) -> int:
    return (end_date - start_date).days // 7 + 1


def is_day_after(day1: int, day2: int) -> bool:
    """Checks if one day of the week is directly after another."""
    return day1 == (day2 + 1) % 7


@dataclass
class PlanGenerator:
    rules: Rules = DEFAULT_RULES

    def generate_training_plan(self, runner: Runner, goal: RaceGoal, start_date: date) -> Plan:
        """Builds a training plan based on coaches design and including limitation rules."""

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

        week_start = plan_start_date
        weeks = []
        week_index = 0
        last_hard_date = None

        while week_start <= race_date_monday:
            sessions = []
            quality_count = 0
            is_race_week = week_start == race_date_monday

            for day in runner.training_days:
                session_date = week_start + timedelta(days=day)
                session_distance = 0.0  # TODO auto distance calc based on rules below

                if (
                    session_date < start_date or session_date >= goal.race_date
                ):  # skips sessions before start date and after race date
                    continue
                elif (
                    is_race_week and day == runner.long_run_day
                ):  # long session becomes easy on race week
                    session_type = "easy"
                elif is_day_after(day, runner.long_run_day) or is_day_after(
                    runner.long_run_day, day
                ):  # session before or after a long run must be easy
                    session_type = "easy"
                elif day == runner.long_run_day:  # runners chosen long run day
                    session_type = "long"
                    last_hard_date = session_date
                elif is_race_week and is_day_after(
                    goal.race_date.weekday(), day
                ):  # session before race must be easy
                    session_type = "easy"
                elif quality_count < max_quality and last_hard_date != session_date - timedelta(
                    days=1
                ):
                    session_type = "tempo" if (week_index + quality_count) % 2 == 0 else "intervals"
                    quality_count += 1
                    last_hard_date = session_date
                else:
                    session_type = "easy"

                sessions.append(
                    Session(
                        date=session_date, session_type=session_type, distance_km=session_distance
                    )
                )

            if is_race_week:
                sessions.append(
                    Session(
                        date=goal.race_date,
                        session_type="race",
                        distance_km=goal.profile.distance_km,
                    )
                )

            weeks.append(Week(start_date=week_start, sessions=(tuple(sessions))))
            week_start += timedelta(weeks=1)
            week_index += 1

        training_plan = Plan(weeks=tuple(weeks))
        return training_plan

    def adapt_training_plan(
        self, plan: Plan, runner: Runner, goal: RaceGoal, actual_km: float
    ) -> Plan: ...
