from dataclasses import dataclass
from scheduler.config import Rules, DEFAULT_RULES
from scheduler.plan import Runner, RaceGoal, Plan
from datetime import date

@dataclass
class PlanGenerator:
    rules: Rules = DEFAULT_RULES

    def generate_training_plan(self, runner: Runner, goal: RaceGoal, start_date: date) -> Plan:
        ...

    def adapt_training_plan(self, plan: Plan, runner: Runner, goal: RaceGoal, actual_km: float) -> Plan:
        ...
