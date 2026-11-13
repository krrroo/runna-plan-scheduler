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
print(week.total_distance())

# after a week of training
actual_km = 18.0  # passed in for now, but idea is that app collects it
planned_km = week.total_distance()
user_wants_update = True  # the runner's decision

if actual_km / planned_km < rules.missed_mileage_threshold:
    if user_wants_update:
        plan = generator.adapt_training_plan(plan, runner, goal, actual_km)
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
| `Week` | start date, sessions | One week of Sessions; `total_distance()` |
| `Plan` | weeks | Full training plan, built with Weeks |
| `WeekDistances` | long, easy, tempo and intervals km for one week | The distance each session type gets that week |
| `PlanGenerator` | rules | Builds a plan that respect the rules; `generate_training_plan(runner, goal, start_date)`, `adapt_training_plan()` (TODO: figure out how adaptation works) |
| `Rules` | max weekly increase, missed-mileage threshold, etc | Rules that each plan has to meet |

## 4. Goal profiles

| Profile | Weeks | Taper weeks | Long run km | Easy km | Tempo km | Intervals km |
|---|---|---|---|---|---|---|
| 5k | 8–12 | 1 | 5 → 8 | 3.5 → 5 | 3.5 → 4.5 | 3.5 → 4 |
| 10k | 10–14 | 1 | 6 → 12 | 4 → 6 | 4 → 5.5 | 3.5 → 5 |
| Half | 12–16 | 2 | 6 → 18 | 4.5 → 7 | 4.5 → 6.5 | 4 → 6 |

Each session type progresses in equal steps from its start to its peak (start → peak), then drops 20% each taper week.

## 5. Rules

| Rule | If broken |
|---|---|
| Every week has easy/tempo/intervals and a long run. Long run doesn't have to happen on a partial sątart week or race week. | Bug in the generator (caught by tests) |
| Race week ends with a race session. | Bug in the generator |
| No tempo or intervals the day after a long run | Bug in the generator (caught by tests) |
| Weekly km rises by at most 10% | Not enforced yet (see open questions) · Warning to the user if they continue after missing mileage |
| Volume tapers down in the final weeks | Bug in the generator (caught by tests) |
| Training plan will only be created if race is more than 50% of training plan min week away | Raise error with info for the user |
| Tempo and intervals will alternate on 3 day plans | Bug in the generator |
| Intervals ≤ tempo ≤ easy distance, every week | Config error (caught by tests) |
| No session below 3.5 km outside the taper | Config error (caught by tests) |
| Long run is the same for every runner on the same plan, whatever their training days | Bug in the generator (caught by tests) |
 
 
## 6. Open questions

- How should the plan update after missed mileage?
- Pace suggestions: where and how are they calculated?
- What happens when a plan breaks the 10% weekly rule?
 