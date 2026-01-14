import numpy as np
import pandas as pd


def make_schedule(teams, k):
    num_teams = len(teams)
    Home = np.repeat(np.repeat(teams, num_teams), k)
    Visitor = np.repeat(np.tile(teams, num_teams), k)
    schedule = pd.DataFrame({"Home": Home, "Visitor": Visitor})
    return schedule.query("Home != Visitor")


def calc_bradley_terry_prob(talent_a, talent_b):
    return np.exp(talent_a) / (np.exp(talent_a) + np.exp(talent_b))


def win_league(season_results):
    # add tiebreakers and calculate league winners
    result = season_results.copy()
    result["wins_adj"] = result["Wins"] + np.random.uniform(0, 1, size=len(result))

    # determine league winners
    max_wins_by_league = result.groupby("lgID")["wins_adj"].max()
    result["win_lg"] = result.apply(
        lambda row: int(row["wins_adj"] == max_wins_by_league[row["lgID"]]), axis=1
    )

    return result


def simulate_one_season(s_talent=0.20, nl_teams=None, al_teams=None, k=9):
    # create team lists and league structure
    if nl_teams is None:
        nl_teams = [
            "ATL",
            "CHN",
            "CIN",
            "HOU",
            "LAN",
            "NYN",
            "PHI",
            "PIT",
            "SFN",
            "SLN",
        ]
    if al_teams is None:
        al_teams = [
            "BAL",
            "BOS",
            "CAL",
            "CHA",
            "CLE",
            "DET",
            "MIN",
            "NYA",
            "OAK",
            "WS2",
        ]

    teams = nl_teams + al_teams
    leagues = ["NL"] * len(nl_teams) + ["AL"] * len(al_teams)

    # validate that we get 162 games per team
    nl_games_per_team = (len(nl_teams) - 1) * k * 2  # *2 for home and away
    al_games_per_team = (len(al_teams) - 1) * k * 2  # *2 for home and away
    if nl_games_per_team != 162:
        print(f"Warning: NL teams will play {nl_games_per_team} games, not 162")
    if al_games_per_team != 162:
        print(f"Warning: AL teams will play {al_games_per_team} games, not 162")

    # create schedule
    nl_schedule = make_schedule(nl_teams, k)
    al_schedule = make_schedule(al_teams, k)
    schedule = pd.concat([nl_schedule, al_schedule], ignore_index=True)

    # simulate talents
    talents = np.random.normal(0, s_talent, len(teams))
    teams_df = pd.DataFrame({"teamID": teams, "lgID": leagues, "talent": talents})

    # merge talents with schedule
    schedule_with_talents = (
        schedule.merge(teams_df, left_on="Home", right_on="teamID")
        .rename(columns={"talent": "talent_home"})
        .merge(
            teams_df,
            left_on="Visitor",
            right_on="teamID",
            suffixes=("", "_visitor"),
        )
        .rename(columns={"talent": "talent_visitor"})
    )

    # calculate home team win probabilities using Bradley-Terry
    schedule_with_talents["prob_home"] = calc_bradley_terry_prob(
        schedule_with_talents["talent_home"],
        schedule_with_talents["talent_visitor"],
    )

    # simulate games
    schedule_with_talents["home_wins"] = np.random.binomial(
        1, schedule_with_talents["prob_home"]
    )
    schedule_with_talents["winner"] = np.where(
        schedule_with_talents["home_wins"] == 1,
        schedule_with_talents["Home"],
        schedule_with_talents["Visitor"],
    )

    # count wins for each team
    win_counts = schedule_with_talents["winner"].value_counts().reset_index()
    win_counts.columns = ["teamID", "Wins"]

    # merge with team info
    results = teams_df.merge(win_counts, on="teamID")

    # simulate postseason
    postseason_results = win_league(results)

    # initialize World Series winner column
    postseason_results["win_ws"] = 0

    # get league champions
    league_champs = postseason_results.query("win_lg == 1").copy()

    # simulate World Series
    if len(league_champs) == 2:
        talent_a, talent_b = league_champs["talent"].values
        prob_a = calc_bradley_terry_prob(talent_a, talent_b)

        # simulate World Series game by game
        wins_a = wins_b = 0
        while wins_a < 4 and wins_b < 4:
            # single Bernoulli trial per game
            game_result = np.random.binomial(1, prob_a)
            if game_result:
                wins_a += 1
            else:
                wins_b += 1

        ws_winner_idx = 0 if wins_a == 4 else 1

        # update the winner
        winner_team = league_champs.iloc[ws_winner_idx]["teamID"]
        postseason_results.loc[
            postseason_results["teamID"] == winner_team, "win_ws"
        ] = 1

    return postseason_results


def display_standings(data, league):
    league_data = data.query(f"lgID == '{league}'")
    total_wins = league_data["Wins"].sum()
    num_teams = len(league_data)
    games_per_team = (2 * total_wins) // num_teams
    return (
        league_data.assign(Losses=lambda x: games_per_team - x["Wins"])[
            ["teamID", "Wins", "Losses"]
        ]
        .sort_values("Wins", ascending=False)
        .reset_index(drop=True)
    )
