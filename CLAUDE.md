# CLAUDE.md

## Project
A small training-plan generator inspired by the Runna app: builds a dated weekly plan
from a runner's training days, race time and race goal (5k, 10k, half marathon).
Design decisions and plan rules: `DESIGN.md` (read only when a change touches plan rules).

## Commands
- Install: `python -m pip install -e ".[dev]"`
- Tests: `pytest` · Lint/format: `ruff check .`, `ruff format .`

## Code review
Review only the PR diff. Report only:
1. **Bugs**: wrong dates, week boundaries, race-week handling, or broken plan rules
   (e.g. two hard sessions on consecutive days).
2. **Missing tests**: a new branch or edge case with no test that would catch a regression.
3. **Design risks**: choices that would block pace calculation, plan adaptation or new goal types.

Skip nits, style and formatting (Ruff enforces them) and test results (pytest runs in CI).
If there's nothing important, post a one-line summary saying so.