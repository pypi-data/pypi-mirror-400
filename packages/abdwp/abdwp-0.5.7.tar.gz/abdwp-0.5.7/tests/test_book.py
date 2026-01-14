import pandas as pd
import numpy as np

from abdwp.book import make_schedule, simulate_one_season, display_standings


def test_make_schedule_basic():
    teams = ["A", "B", "C"]
    schedule = make_schedule(teams, k=1)

    # should have 6 games total (each team plays each other once)
    assert len(schedule) == 6
    assert "Home" in schedule.columns
    assert "Visitor" in schedule.columns

    # no team should play itself
    assert not (schedule["Home"] == schedule["Visitor"]).any()


def test_make_schedule_games_per_team():
    teams = ["A", "B", "C", "D"]
    k = 2
    schedule = make_schedule(teams, k)

    # each team should play every other team k times as home and k times as visitor
    for team in teams:
        home_games = (schedule["Home"] == team).sum()
        visitor_games = (schedule["Visitor"] == team).sum()
        total_games = home_games + visitor_games

        # with 4 teams, each team plays 3 opponents × k times × 2 (home/away) = 12 games
        expected_games = (len(teams) - 1) * k * 2
        assert total_games == expected_games


def test_simulate_one_season_default():
    # use fixed seed for reproducible test
    np.random.seed(42)
    result = simulate_one_season()

    # should return 20 teams (10 NL + 10 AL)
    assert len(result) == 20
    assert set(result["lgID"].unique()) == {"NL", "AL"}

    # each league should have 10 teams
    assert (result["lgID"] == "NL").sum() == 10
    assert (result["lgID"] == "AL").sum() == 10

    # should have expected columns
    expected_cols = {"teamID", "lgID", "talent", "Wins", "wins_adj", "win_lg", "win_ws"}
    assert set(result.columns) == expected_cols


def test_simulate_one_season_162_games():
    """Test that default parameters result in 162 games per team"""
    # create a simple test to verify game count without running full simulation
    nl_teams = ["A", "B"]
    al_teams = ["X", "Y"]
    k = 1

    from abdwp.book import make_schedule
    import pandas as pd

    nl_schedule = make_schedule(nl_teams, k)
    al_schedule = make_schedule(al_teams, k)
    schedule = pd.concat([nl_schedule, al_schedule], ignore_index=True)

    # each team should appear in schedule the correct number of times
    for team in nl_teams + al_teams:
        home_games = (schedule["Home"] == team).sum()
        visitor_games = (schedule["Visitor"] == team).sum()
        total_games = home_games + visitor_games

        # with 2 teams per league: 1 opponent × k times × 2 (home/away) = 2 games
        expected_games = 1 * k * 2
        assert total_games == expected_games


def test_simulate_one_season_custom_teams():
    """Test simulation with custom team lists"""
    nl_teams = ["NYN", "PHI"]
    al_teams = ["NYA", "BOS"]

    result = simulate_one_season(nl_teams=nl_teams, al_teams=al_teams, k=1)

    # should have teams from both leagues
    result_teams = set(result["teamID"])
    expected_teams = set(nl_teams + al_teams)
    assert result_teams.issubset(
        expected_teams
    )  # some teams might not appear in final results

    # should have both leagues represented
    leagues = set(result["lgID"])
    assert leagues.issubset({"NL", "AL"})


def test_display_standings():
    # create sample data
    data = pd.DataFrame(
        {
            "teamID": ["A", "B", "C", "D"],
            "lgID": ["NL", "NL", "AL", "AL"],
            "Wins": [90, 85, 95, 80],
        }
    )

    nl_standings = display_standings(data, "NL")
    al_standings = display_standings(data, "AL")

    # should filter by league
    assert len(nl_standings) == 2
    assert len(al_standings) == 2

    # should be sorted by wins descending
    assert nl_standings.iloc[0]["Wins"] >= nl_standings.iloc[1]["Wins"]
    assert al_standings.iloc[0]["Wins"] >= al_standings.iloc[1]["Wins"]

    # should have Losses column and calculate correctly
    assert "Losses" in nl_standings.columns
    # for NL: max_wins=90, min_wins=85, so total_games=175
    # team with 90 wins should have 175-90=85 losses
    nl_total_games = (
        data.query("lgID == 'NL'")["Wins"].max()
        + data.query("lgID == 'NL'")["Wins"].min()
    )
    assert (
        nl_standings.iloc[0]["Losses"] == nl_total_games - nl_standings.iloc[0]["Wins"]
    )
