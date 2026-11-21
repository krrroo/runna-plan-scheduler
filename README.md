# runna-plan-scheduler
The project: a training-plan scheduler. Given a goal (5k, 10k, half), a race date, available days and a current 5k time, it generates a weekly plan, then adapts when a session is missed.

## Run it

```bash
pip install -e ".[dev]"
python -m scheduler --goal half --race-date 2027-03-14 --days tue,thu,sat,sun --long-run-day sun --start-date 2026-12-07
```

Options:

- `--goal`: the race distance
  - 5k: `5k` or `5km`
  - 10k: `10k` or `10km`
  - Half marathon: `half`, `half-marathon`, `21k`, `21km`, `21.1k`, `21.1km` or `"half marathon"`
- `--race-date`: `YYYY-MM-DD`
- `--days`: training days, min 3, `tue,thu,sun` or `tuesday,thursday,sunday`
- `--long-run-day`: one of the training days, e.g. `sun`
- `--start-date`: `YYYY-MM-DD`
- `--race-time`: default: 30:00
- `--race-distance`: default: 5 km

Run `python -m scheduler --help` for details.

## Test it

```bash
pytest
```