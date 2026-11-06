from dataclasses import dataclass
from scheduler.config import Rules, DEFAULT_RULES
from scheduler.plan import Runner, RaceGoal, Plan, Week
from datetime import date, timedelta

def monday_of_week_date(date: date) -> date:
    """Returns a Monday of a week from a given date"""
    return date - timedelta(days = date.weekday())

def weeks_in_plan(start_date: date, end_date:date) -> date:
    return (end_date-start_date).days // 7 + 1

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

        if plan_weeks <= min_plan_weeks/2:
            raise ValueError('Your race is too soon to train for safely. Please choose a different race goal.')
        elif plan_weeks > max_plan_weeks:
            plan_max_diff = plan_weeks - max_plan_weeks
            plan_start_date = plan_start_week_monday + timedelta(weeks=plan_max_diff)
        else:
            plan_start_date = plan_start_week_monday

        start = plan_start_date
        weeks = []
        while start <= race_date_monday:
            weeks.append(Week(start_date = start, sessions=()))
            start += timedelta(weeks=1)

        training_plan = Plan(weeks=tuple(weeks))
        return training_plan


    def adapt_training_plan(self, plan: Plan, runner: Runner, goal: RaceGoal, actual_km: float) -> Plan:
        ...
