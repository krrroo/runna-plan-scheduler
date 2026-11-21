import pytest

from scheduler.__main__ import main

BASE_ARGS = [
    "--goal",
    "5k",
    "--race-date",
    "2027-03-07",
    "--days",
    "tue,thu,sun",
    "--long-run-day",
    "sun",
]


def test_cli_prints_plan(capsys):
    code = main(BASE_ARGS + ["--start-date", "2026-12-14"])
    output = capsys.readouterr().out
    assert code == 0
    assert "Week 1" in output
    assert "race" in output


def test_cli_accepts_full_day_names_and_half_marathon(capsys):
    code = main(
        [
            "--goal",
            "half marathon",
            "--race-date",
            "2027-03-14",
            "--days",
            "tuesday,thursday,saturday,sunday",
            "--long-run-day",
            "sunday",
            "--start-date",
            "2026-12-07",
        ]
    )
    assert code == 0
    assert "HalfMarathon plan" in capsys.readouterr().out


def test_cli_reports_race_too_soon(capsys):
    # 4 weeks before a 5k race: at or below half the 8-week minimum
    code = main(BASE_ARGS + ["--start-date", "2027-02-14"])
    error = capsys.readouterr().err
    assert code == 1
    assert "too soon" in error


def test_cli_rejects_unknown_day():
    with pytest.raises(SystemExit) as exit_info:
        main(
            [
                "--goal",
                "5k",
                "--race-date",
                "2027-03-07",
                "--days",
                "tue,funday",
                "--long-run-day",
                "sun",
            ]
        )
    assert exit_info.value.code == 2


def test_cli_rejects_unsupported_goal(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(
            [
                "--goal",
                "marathon",
                "--race-date",
                "2027-03-07",
                "--days",
                "tue,thu,sun",
                "--long-run-day",
                "sun",
            ]
        )
    assert exit_info.value.code == 2
    assert "Please choose a different goal than 'marathon'" in capsys.readouterr().err


def test_cli_reports_zero_race_time(capsys):
    code = main(BASE_ARGS + ["--race-time", "0:00"])
    assert code == 1
    assert "Race time" in capsys.readouterr().err
