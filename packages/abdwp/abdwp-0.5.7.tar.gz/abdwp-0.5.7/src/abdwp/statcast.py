import concurrent.futures
import io
import time
import warnings
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from tqdm.auto import tqdm

_URL = (
    "https://baseballsavant.mlb.com/statcast_search/csv"
    "?all=true&type=details"
    "&game_date_gt={start_date}&game_date_lt={end_date}"
)


def _process_dates(start_date: str | None, end_date: str | None) -> tuple[date, date]:
    if start_date is None and end_date is None:
        today = date.today()
        return today - timedelta(days=1), today

    start_date = start_date or end_date
    end_date = end_date or start_date

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as e:
        raise ValueError("date must be in YYYY-MM-DD format") from e

    if end < start:
        raise ValueError("end_date must be after start_date")

    return start, end


def _get_data_for_date(dt: date) -> pd.DataFrame:
    url = _URL.format(start_date=dt, end_date=dt)

    for attempt in range(3):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt == 2:
                raise
            time.sleep(2**attempt)

    if not response.text:
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(response.text))

    if "error" in df.columns:
        raise RuntimeError(df["error"].values[0])

    return df


def statcast(
    start_date: str | None = None,
    end_date: str | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Collect Statcast pitch-level data from Baseball Savant.

    Parameters
    ----------
    start_date : str, optional
        start date in YYYY-MM-DD format
    end_date : str, optional
        end date in YYYY-MM-DD format
    verbose : bool, default True
        print progress updates

    Returns
    -------
    pd.DataFrame
        Statcast data for the specified date range
    """
    no_dates_supplied = start_date is None and end_date is None
    start, end = _process_dates(start_date, end_date)

    if verbose and no_dates_supplied:
        print(f"No dates supplied. Collecting data for {start}.")

    dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    results: list[pd.DataFrame] = []

    with tqdm(total=len(dates), disable=not verbose, desc="Downloading") as progress:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(_get_data_for_date, dt) for dt in dates}
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
                progress.update(1)

    results = [r for r in results if not r.empty]

    if not results:
        warnings.warn("No data found for the specified date range!", UserWarning)
        return pd.DataFrame()

    # currently not converting to string type to match pybaseball
    # string type uses pd.NA, so if we use string, might consider
    # switching from dtype_backend="numpy_nullable" to "pyarrow"
    df = pd.concat(results, axis=0).convert_dtypes(convert_string=False)
    df["game_date"] = pd.to_datetime(df["game_date"], format="ISO8601")

    # this ordering is newest-first, to match pybaseball
    df = df.sort_values(
        ["game_date", "game_pk", "at_bat_number", "pitch_number"],
        ascending=False,
    )

    return df


def _check_file_age(path: Path) -> None:
    """warn if file is older than a year."""
    mod_time = datetime.fromtimestamp(path.stat().st_mtime)
    one_year_ago = datetime.now() - timedelta(days=365)
    if mod_time < one_year_ago:
        warnings.warn(
            f"File is over a year old (last modified: {mod_time.strftime('%Y-%m-%d')}). "
            "Statcast data may change over time. Consider re-downloading with force_download=True.",
            UserWarning,
            stacklevel=3,
        )


def download_seasons(
    start_year: int,
    end_year: int | None = None,
    force_download: bool = False,
    data_dir: str = "statcast",
    verbose: bool = True,
) -> None:
    """
    Download full seasons of Statcast data and save as parquet files.

    Parameters
    ----------
    start_year : int
        first year to download
    end_year : int, optional
        last year to download (defaults to start_year)
    force_download : bool, default False
        re-download even if file exists
    data_dir : str, default "statcast"
        directory to save parquet files
    verbose : bool, default True
        print progress updates
    """
    if end_year is None:
        end_year = start_year

    if not isinstance(start_year, int) or not isinstance(end_year, int):
        raise TypeError("start_year and end_year must be integers")

    if start_year > end_year:
        raise ValueError("start_year must be less than or equal to end_year")

    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    for year in range(start_year, end_year + 1):
        parquet_path = data_path / f"statcast-{year}.parquet"
        if parquet_path.exists() and not force_download:
            if verbose:
                print(f"Data for {year} already exists, skipping.")
        else:
            if verbose:
                print(f"Downloading data for {year}.")
            df = statcast(
                start_date=f"{year}-01-01", end_date=f"{year}-12-31", verbose=verbose
            )
            df.to_parquet(
                parquet_path, index=False, engine="pyarrow", compression="zstd"
            )


def load_season(
    year: int,
    force_download: bool = False,
    regular_season: bool = False,
    data_dir: str = "statcast",
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Load a season of Statcast data, downloading if necessary.

    Parameters
    ----------
    year : int
        season year to load
    force_download : bool, default False
        re-download even if file exists
    regular_season : bool, default False
        filter to regular season games only
    data_dir : str, default "statcast"
        directory containing parquet files
    verbose : bool, default True
        print progress updates

    Returns
    -------
    pd.DataFrame
        Statcast data for the specified season
    """
    parquet_path = Path(data_dir) / f"statcast-{year}.parquet"

    if force_download or not parquet_path.exists():
        download_seasons(
            year,
            year,
            force_download=force_download,
            data_dir=data_dir,
            verbose=verbose,
        )

    _check_file_age(parquet_path)
    df = pd.read_parquet(parquet_path, engine="pyarrow")

    if regular_season:
        df = df[df["game_type"] == "R"]

    return df


# all statcast features as of july 2025
statcast_features_all = [
    "pitch_type",
    "game_date",
    "release_speed",
    "release_pos_x",
    "release_pos_z",
    "player_name",
    "batter",
    "pitcher",
    "events",
    "description",
    "spin_dir",
    "spin_rate_deprecated",
    "break_angle_deprecated",
    "break_length_deprecated",
    "zone",
    "des",
    "game_type",
    "stand",
    "p_throws",
    "home_team",
    "away_team",
    "type",
    "hit_location",
    "bb_type",
    "balls",
    "strikes",
    "game_year",
    "pfx_x",
    "pfx_z",
    "plate_x",
    "plate_z",
    "on_3b",
    "on_2b",
    "on_1b",
    "outs_when_up",
    "inning",
    "inning_topbot",
    "hc_x",
    "hc_y",
    "tfs_deprecated",
    "tfs_zulu_deprecated",
    "umpire",
    "sv_id",
    "vx0",
    "vy0",
    "vz0",
    "ax",
    "ay",
    "az",
    "sz_top",
    "sz_bot",
    "hit_distance_sc",
    "launch_speed",
    "launch_angle",
    "effective_speed",
    "release_spin_rate",
    "release_extension",
    "game_pk",
    "fielder_2",
    "fielder_3",
    "fielder_4",
    "fielder_5",
    "fielder_6",
    "fielder_7",
    "fielder_8",
    "fielder_9",
    "release_pos_y",
    "estimated_ba_using_speedangle",
    "estimated_woba_using_speedangle",
    "woba_value",
    "woba_denom",
    "babip_value",
    "iso_value",
    "launch_speed_angle",
    "at_bat_number",
    "pitch_number",
    "pitch_name",
    "home_score",
    "away_score",
    "bat_score",
    "fld_score",
    "post_away_score",
    "post_home_score",
    "post_bat_score",
    "post_fld_score",
    "if_fielding_alignment",
    "of_fielding_alignment",
    "spin_axis",
    "delta_home_win_exp",
    "delta_run_exp",
    "bat_speed",
    "swing_length",
    "estimated_slg_using_speedangle",
    "delta_pitcher_run_exp",
    "hyper_speed",
    "home_score_diff",
    "bat_score_diff",
    "home_win_exp",
    "bat_win_exp",
    "age_pit_legacy",
    "age_bat_legacy",
    "age_pit",
    "age_bat",
    "n_thruorder_pitcher",
    "n_priorpa_thisgame_player_at_bat",
    "pitcher_days_since_prev_game",
    "batter_days_since_prev_game",
    "pitcher_days_until_next_game",
    "batter_days_until_next_game",
    "api_break_z_with_gravity",
    "api_break_x_arm",
    "api_break_x_batter_in",
    "arm_angle",
    "attack_angle",
    "attack_direction",
    "swing_path_tilt",
    "intercept_ball_minus_batter_pos_x_inches",
    "intercept_ball_minus_batter_pos_y_inches",
]


# h/t to scott powers
_statcast_features_reorder = [
    # pitch identifiers
    "game_pk",
    "game_date",
    "game_type",
    "game_year",
    "at_bat_number",
    "pitch_number",
    # player and team identifiers
    "home_team",
    "away_team",
    "batter",
    "stand",
    "player_name",
    "pitcher",
    "p_throws",
    "on_1b",
    "on_2b",
    "on_3b",
    "fielder_2",
    "fielder_3",
    "fielder_4",
    "fielder_5",
    "fielder_6",
    "fielder_7",
    "fielder_8",
    "fielder_9",
    # context
    "inning",
    "inning_topbot",
    "outs_when_up",
    "balls",
    "strikes",
    "if_fielding_alignment",
    "of_fielding_alignment",
    # pitch tracking
    "pitch_type",
    "arm_angle",
    ## features needed to recreate the full quadratic trajectory of the pitch
    "ax",
    "ay",
    "az",
    "vx0",
    "vy0",
    "vz0",
    "release_pos_x",
    "release_pos_y",
    "release_pos_z",
    ## interpretable features that are functions of the quadratic trajectory
    "release_speed",
    "release_extension",
    "effective_speed",
    "pfx_x",
    "pfx_z",
    "plate_x",
    "plate_z",
    "zone",
    ## additional features not derived from the quadratic trajectory
    "release_spin_rate",
    "spin_axis",
    "sz_top",
    "sz_bot",
    # swing tracking
    "bat_speed",
    "swing_length",
    "attack_angle",
    "attack_direction",
    "swing_path_tilt",
    "intercept_ball_minus_batter_pos_x_inches",
    "intercept_ball_minus_batter_pos_y_inches",
    # batted ball tracking
    "launch_speed",
    "launch_angle",
    "estimated_woba_using_speedangle",
    "estimated_ba_using_speedangle",
    "estimated_slg_using_speedangle",
    "hc_x",
    "hc_y",
    "hit_distance_sc",
    "bb_type",
    "hit_location",
    # outcome
    "type",
    "description",
    "events",
    "woba_denom",
    "woba_value",
    "babip_value",
    "iso_value",
    "delta_run_exp",
    "delta_home_win_exp",
]


_statcast_features_remove = [
    feature
    for feature in statcast_features_all
    if feature not in _statcast_features_reorder
]

statcast_features_ordered = _statcast_features_reorder + _statcast_features_remove


def reorder_columns(df, keep_all=False, inplace=False):
    df = df if inplace else df.copy()
    df = df.loc[:, statcast_features_ordered]
    if not keep_all:
        df.drop(_statcast_features_remove, axis=1, errors="ignore", inplace=True)
    return None if inplace else df


# TODO: note that game *time* is not considered
# TODO: add uid for unique at-bat and pitch?
def order_pitches(df, keep_index=False, ascending=True, inplace=False):
    df = df if inplace else df.copy()
    sort_columns = ["game_date", "game_pk", "at_bat_number", "pitch_number"]
    missing = [col for col in sort_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"DataFrame is missing required columns for sorting: {missing}"
        )
    df.sort_values(by=sort_columns, ascending=ascending, inplace=True)
    if not keep_index:
        df.reset_index(drop=True, inplace=True)
    return None if inplace else df


def filter_regular_season(df, inplace=False):
    df = df if inplace else df.copy()
    if "game_type" not in df.columns:
        raise ValueError("DataFrame must contain a 'game_type' column.")
    regular_season_mask = df["game_type"] == "R"
    df.drop(df[~regular_season_mask].index, inplace=True)
    return None if inplace else df


def add_transformed_hit_locations(df, inplace=False):
    df = df if inplace else df.copy()
    a_x, b_x = (-301.777, 2.41036)
    a_y, b_y = (490.267, -2.41036)
    df["hit_x"] = a_x + b_x * df["hc_x"]
    df["hit_y"] = a_y + b_y * df["hc_y"]
    return None if inplace else df


def add_names(df, remove_player=False, inplace=False):
    df = df if inplace else df.copy()
    df["batter_name"] = lookup_name(df["batter"])
    df["pitcher_name"] = lookup_name(df["pitcher"])
    if remove_player:
        df.drop("player_name", axis=1, inplace=True)
    return None if inplace else df


_chadwick_columns = [
    # "key_person",
    # "key_uuid",
    "key_mlbam",
    "key_retro",
    "key_bbref",
    # "key_bbref_minors",
    "key_fangraphs",
    "key_npb",
    # "key_wikidata",
    "name_last",
    "name_first",
    "name_given",
    "name_suffix",
    "name_matrilineal",
    "birth_year",
    "birth_month",
    "birth_day",
    # "death_year",
    # "death_month",
    # "death_day",
]


# TODO* could consider adding lahman keys to this table
def _make_chadwick_people_table():
    chadwick_urls = [
        (
            "https://raw.githubusercontent.com/"
            "chadwickbureau/register/master/data/"
            f"people-{c}.csv"
        )
        for c in list(map(str, range(10))) + list("abcdef")
    ]

    def read_csv(url):
        return pd.read_csv(
            url,
            usecols=_chadwick_columns,
            dtype_backend="numpy_nullable",
            engine="pyarrow",
        )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        dataframes = list(executor.map(read_csv, chadwick_urls))

    data = pd.concat(dataframes, ignore_index=True)
    data = data[data["key_mlbam"].notna()]
    return data


_chadwick_people = None


def _get_chadwick_people():
    global _chadwick_people
    if _chadwick_people is None:
        _chadwick_people = _make_chadwick_people_table()
    return _chadwick_people


def lookup_name(mlbam_id):
    # get people df
    people = _get_chadwick_people()

    # build name from components
    def name_for_row(row):
        first = row.get("name_first", "")
        if pd.isna(first):
            first = ""
        last = row.get("name_last", "")
        if pd.isna(last):
            last = ""
        suffix = row.get("name_suffix", "")
        if pd.isna(suffix):
            suffix = ""
        parts = [
            part.strip() for part in [first, last, suffix] if part and str(part).strip()
        ]
        return " ".join(parts) if parts else ""

    # build fast lookup mapping
    if not hasattr(lookup_name, "_id_to_name"):
        valid_people = people[people["key_mlbam"].notna()].copy()
        if len(valid_people) > 0:
            # vectorized name construction
            names = valid_people.apply(name_for_row, axis=1)
            ids = valid_people["key_mlbam"].astype(int)
            lookup_name._id_to_name = dict(zip(ids, names))
        else:
            lookup_name._id_to_name = {}
    id_to_name = lookup_name._id_to_name

    # handle different input types
    if isinstance(mlbam_id, int):
        return id_to_name.get(mlbam_id, None)
    elif isinstance(mlbam_id, list):
        if not mlbam_id:  # empty list
            return []
        # validate all items are integers
        try:
            return [id_to_name.get(int(mid), None) for mid in mlbam_id]
        except (ValueError, TypeError) as e:
            raise ValueError(f"All items in list must be convertible to integers: {e}")
    elif isinstance(mlbam_id, pd.Series):
        if len(mlbam_id) == 0:  # empty series
            return []
        # check if series contains integer-like data
        if not (
            pd.api.types.is_integer_dtype(mlbam_id)
            or pd.api.types.is_extension_array_dtype(mlbam_id)
        ):
            raise TypeError("pandas Series must have integer dtype")

        # convert each value, handling NaN appropriately
        result = []
        for value in mlbam_id:
            if pd.isna(value):
                result.append(None)
            else:
                try:
                    result.append(id_to_name.get(int(value), None))
                except (ValueError, TypeError):
                    raise ValueError(f"Cannot convert Series value {value} to integer")
        return result
    else:
        raise TypeError(
            "mlbam_id must be an integer, a list of integers, or an integer pandas Series."
        )


def clear_name_cache():
    """
    Clear the cached player name lookup dictionary.

    This can be useful if the underlying Chadwick data has been updated
    or to free up memory in long-running applications.
    """
    if hasattr(lookup_name, "_id_to_name"):
        delattr(lookup_name, "_id_to_name")


def lookup_id(name_last, name_first, last_only=False, fuzzy=False):
    people = _get_chadwick_people()
    if not name_last:
        raise ValueError("name_last cannot be empty")
    if not last_only and not name_first:
        raise ValueError("name_first cannot be empty when last_only=False")
    name_last_people = people["name_last"].fillna("").str.lower()
    name_first_people = people["name_first"].fillna("").str.lower()
    name_first = str(name_first).strip().lower() if name_first else ""
    name_last = str(name_last).strip().lower()
    last_mask = name_last_people == name_last
    if last_only:
        if fuzzy and not last_mask.any():
            last_fuzzy = name_last_people.str.contains(name_last, na=False, regex=False)
            return people.loc[last_fuzzy]
        return people.loc[last_mask]
    first_mask = name_first_people == name_first
    full_mask = last_mask & first_mask
    if fuzzy and not full_mask.any():
        last_fuzzy = name_last_people.str.contains(name_last, na=False, regex=False)
        first_fuzzy = name_first_people.str.contains(name_first, na=False, regex=False)
        fuzzy_mask = last_fuzzy & first_fuzzy
        return people.loc[fuzzy_mask]
    return people.loc[full_mask]
