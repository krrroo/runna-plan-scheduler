# Training Plan Scheduler: Design

## 1. Scope

**To build:** 5k, 10k and Half Marathon goals · dated plans ending on race day · training plan rules · missed mileage adaptation (the runner chooses to update the plan or continue)

**Skip (for now):** weather adaptation · feeling unwell adaptation · auto plan updates · storage and UI

## 2. Usage example

```python
runner = Runner(...)
goal = RaceGoal(profile=PLAN_HALF_MARATHON, race_date=date(2027, 3, 8))
rules = DEFAULT_RULES  # coach designed limitations TBC how stored

generator = PlanGenerator(rules)
plan = generator.generate_training_plan(runner, goal, start_date=date(2026, 12, 7))

week = plan.weeks[0]
print(week.total_plan_distance())

# after a week of training
runs = [
    CompletedRun(date=date(2026, 12, 8), distance_km=4.0)
]  # passed in for now, but idea is that app collects it
user_wants_update = True  # the runner's decision

if generator.is_shortfall(week, runs):
    if user_wants_update:
        plan = generator.adapt_training_plan(plan, week_index=0, runs=runs)
    else:
        print(
            "Warning: next week jumps more than 10% above what you ran. Continue at your own risk."
        )
```

## 3. Classes

| Class | Holds | Responsibility |
|---|---|---|
| `Runner` | current race distance and time, training days, long-run day | Runner's characteristics |
| `GoalProfile` | distance, min/max weeks, taper weeks, start and peak km for long run, easy, tempo and intervals | The coach's training plan characteristics |
| `RaceGoal` | profile, race date | What the runner is aiming for, and when |
| `Session` | date, session type (`Literal["easy", "tempo", "intervals", "long", "race"]`), distance km | One planned run |
| `Week` | start date, sessions | One week of Sessions; `total_plan_distance()`, `total_actual_distance(runs)` |
| `Plan` | weeks | Full training plan, built with Weeks |
| `WeekDistances` | long, easy, tempo and intervals km for one week | The distance each session type gets that week |
| `CompletedRun` | date, distance km | A run the runner actually did (activity log, kept separate from the plan) |
| `PlanGenerator` | rules | Builds a plan that respect the rules; `generate_training_plan(runner, goal, start_date)`, `is_shortfall(week, runs)`, `adapt_training_plan(plan, week_index, runs)` |
| `Rules` | max weekly increase, missed-mileage threshold, max adapt decrease, etc | Rules that each plan has to meet |
 
## 4. Goal profiles

| Profile | Weeks | Taper weeks | Long run km | Easy km | Tempo km | Intervals km |
|---|---|---|---|---|---|---|
| 5k | 8–12 | 1 | 5 → 8 | 3.5 → 5 | 3.5 → 4.5 | 3.5 → 4 |
| 10k | 10–14 | 1 | 6 → 12 | 4 → 6 | 4 → 5.5 | 3.5 → 5 |
| Half | 12–16 | 2 | 6 → 18 | 4.5 → 7 | 4.5 → 6.5 | 4 → 6 |

Each session type progresses in equal steps from its start to its peak (start → peak), then drops 20% each taper week.

## 5. Rules

Plan rules are checked by unit tests and by Hypothesis property tests.

| Rule | If broken |
|---|---|
| Every week has easy/tempo/intervals and a long run. Long run doesn't have to happen on a partial sątart week or race week. | Bug in the generator (caught by tests) |
| Race week ends with a race session. | Bug in the generator |
| No tempo or intervals the day after a long run | Bug in the generator (caught by tests) |
| The day before the race is easy, including when it falls in the previous week (e.g. a Monday race) | Bug in the generator (caught by unit and property tests) |
| Weekly km rises by at most 10% | Not enforced yet (see open questions) · Warning to the user if they continue after missing mileage |
| Volume tapers down in the final weeks | Bug in the generator (caught by tests) |
| Training plan will only be created if race is more than 50% of training plan min week away | Raise error with info for the user |
| Tempo and intervals will alternate on 3 day plans | Bug in the generator |
| Intervals ≤ tempo ≤ easy distance, every week | Config error (caught by tests) |
| No session below 3.5 km outside the taper, in generated plans (adapted plans may go below) | Config error (caught by tests) |
| Long run is the same for every runner on the same plan, whatever their training days | Bug in the generator (caught by tests) |
| Runner is offered adaptation only if they completed under 90% of a week's planned km, and only adapts if they choose to | `is_shortfall` returns False · no adaptation offered |
| Adapting cuts each later week's total by at most 20%; long runs and the race stay the same; the missed week and earlier weeks are unchanged | Bug in the generator (caught by tests) |
| Adaptation called without a shortfall | Raise error |
 
 
## 6. Open questions

- Pace suggestions: where and how are they calculated?
- What happens when a plan breaks the 10% weekly rule?
- Limit adaptation: max number of adaptations, minimum weeks between them, or a floor relative to the original plan?
 