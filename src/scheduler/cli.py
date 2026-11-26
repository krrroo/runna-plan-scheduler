import argparse
import sys
from datetime import date, timedelta

from scheduler.config import PLAN_5K, PLAN_10K, PLAN_HALF_MARATHON
from scheduler.generator import PlanGenerator
from scheduler.plan import Plan, RaceGoal, Runner

GOALS = {
    "5k": PLAN_5K,
    "5km": PLAN_5K,
    "10k": PLAN_10K,
    "10km": PLAN_10K,
    "half": PLAN_HALF_MARATHON,
    "21k": PLAN_HALF_MARATHON,
    "21km": PLAN_HALF_MARATHON,
    "21.1k": PLAN_HALF_MARATHON,
    "21.1km": PLAN_HALF_MARATHON,
    "half marathon": PLAN_HALF_MARATHON,
    "half-marathon": PLAN_HALF_MARATHON,
}
DAYS = {
    "mon": 0,
    "monday": 0,
    "tue": 1,
    "tuesday": 1,
    "wed": 2,
    "wednesday": 2,
    "thu": 3,
    "thursday": 3,
    "fri": 4,
    "friday": 4,
    "sat": 5,
    "saturday": 5,
    "sun": 6,
    "sunday": 6,
}


def parse_day(text: str) -> int:
    """Turns day name into day int."""
    name = text.strip().lower()
    if name not in DAYS:
        raise argparse.ArgumentTypeError(
            f"Unknown day '{text}'. Use a day name like mon or monday."
        )
    return DAYS[name]


def parse_days(text: str) -> tuple[int, ...]:
    """Sorts 'tue,thu,sun' into (1, 3, 6)."""
    return tuple(sorted(parse_day(name) for name in text.split(",")))


def parse_goal(text: str):
    """Turns user input goal into its goal profile."""
    name = text.strip().lower()
    if name not in GOALS:
        raise argparse.ArgumentTypeError(
            f"Please choose a different goal than '{text}'. Supported plans: 5k, 10k, half marathon."
        )
    return GOALS[name]


def parse_date(text: str) -> date:
    """Turns '2027-03-14' into a date."""
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date '{text}'. Use YYYY-MM-DD.") from None


def parse_race_time(text: str) -> timedelta:
    """Turns '30:12' (MM:SS) or '1:02:55' (H:MM:SS) into a timedelta."""
    try:
        parts = [int(part) for part in text.split(":")]
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid time '{text}'. Use MM:SS or H:MM:SS.") from None
    if len(parts) == 2:
        minutes, seconds = parts
        return timedelta(minutes=minutes, seconds=seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    raise argparse.ArgumentTypeError(f"Invalid time '{text}'. Use MM:SS or H:MM:SS.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scheduler", description="Generate a running training plan."
    )
    parser.add_argument("--goal", required=True, type=parse_goal, help="5k, 10k or half marathon")
    parser.add_argument("--race-date", required=True, type=parse_date, help="YYYY-MM-DD")
    parser.add_argument(
        "--days", required=True, type=parse_days, help="training days, e.g. tue,thu,sat,sun"
    )
    parser.add_argument("--long-run-day", required=True, type=parse_day, help="e.g. sun or sunday")
    parser.add_argument(
        "--start-date", type=parse_date, default=date.today(), help="YYYY-MM-DD (default: today)"
    )
    parser.add_argument(
        "--race-time",
        type=parse_race_time,
        default=timedelta(minutes=30),
        help="recent race time, MM:SS or H:MM:SS (default: 30:00)",
    )
    parser.add_argument(
        "--race-distance",
        type=float,
        default=5.0,
        help="recent race distance in km (default: 5)",
    )
    parser.add_argument(
        "--time-zone",
        default="Europe/London",
        help="IANA time zone, e.g. Europe/London (default: Europe/London)",
    )
    return parser


def format_plan(plan: Plan, goal: RaceGoal) -> str:
    """Formats the plan as readable text, week by week."""
    lines = [f"{goal.profile.name} plan · race on {goal.race_date:%a %d %b %Y}", ""]
    for number, week in enumerate(plan.weeks, start=1):
        lines.append(
            f"Week {number} · {week.start_date:%a %d %b} · {week.total_plan_distance():.1f} km"
        )
        for session in week.sessions:
            lines.append(
                f"  {session.date:%a %d %b}   {session.session_type:<10} {session.distance_km:>5.1f} km"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Runs the CLI. Returns 0 on success, 1 if the plan can't be built."""
    args = build_parser().parse_args(argv)
    try:
        runner = Runner(
            runner_id="cli",
            current_race_distance_km=args.race_distance,
            current_race_time=args.race_time,
            training_days=args.days,
            long_run_day=args.long_run_day,
            time_zone=args.time_zone,
        )
        goal = RaceGoal(profile=args.goal, race_date=args.race_date)
        plan = PlanGenerator().generate_training_plan(runner, goal, args.start_date)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(format_plan(plan, goal))
    return 0
