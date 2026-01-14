import os
import pandas as pd
from typing import Optional


def glimpse(
    df: pd.DataFrame,
    col_width: Optional[int] = None,
    type_width: Optional[int] = None,
    num_examples: int = 5,
) -> None:
    """
    Display a compact overview of a DataFrame, similar to R's dplyr::glimpse().

    Shows DataFrame dimensions, column names, data types, and sample values
    in a format that adapts to terminal width.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to display
    col_width : int, optional
        Maximum width for column name display. If None, calculated from data
    type_width : int, optional
        Width for data type display. If None, calculated from data
    num_examples : int, default 5
        Number of example values to show for each column

    Raises
    ------
    TypeError
        If df is not a pandas DataFrame
    ValueError
        If num_examples is negative
    """
    # input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")

    if num_examples < 0:
        raise ValueError("num_examples must be non-negative")

    # handle empty DataFrame
    if df.empty:
        print("Empty DataFrame")
        print("Rows: 0")
        print("Columns: 0")
        return

    # get terminal width with better error handling
    try:
        terminal_width = os.get_terminal_size().columns
    except (OSError, ValueError):
        # fallback for non-terminal environments or Windows issues
        terminal_width = 120

    # calculate display widths if not provided
    if col_width is None:
        col_width = max(len(col) for col in df.columns) if len(df.columns) > 0 else 10

    if type_width is None:
        type_width = (
            max(len(str(df[col].dtype)) for col in df.columns)
            if len(df.columns) > 0
            else 10
        )

    # ensure minimum widths for readability
    col_width = max(col_width, 5)
    type_width = max(type_width, 5)

    # display DataFrame info
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]:,}")
    print()

    # ANSI codes for bold text
    BOLD_START = "\033[1m"
    BOLD_END = "\033[0m"
    ANSI_CODE_LENGTH = len(BOLD_START) + len(BOLD_END)

    # display each column
    for col in df.columns:
        # truncate column name if too long
        if len(col) > col_width:
            col_display = col[: col_width - 1] + "…"
        else:
            col_display = col

        # create bold column name with proper spacing
        col_display_bold = f"{BOLD_START}{col_display}{BOLD_END}"
        # pad with spaces accounting for ANSI codes
        column_section = f"{col_display_bold:<{col_width + ANSI_CODE_LENGTH}}"

        # format data type
        dtype_section = f"{str(df[col].dtype):<{type_width}}"

        # get sample values
        sample_values = df[col].head(num_examples).tolist()
        values_section = str(sample_values)

        # combine all sections
        line = f"{column_section} {dtype_section} {values_section}"

        # truncate line if too long for terminal
        if len(line) > terminal_width:
            # account for "..." at the end
            max_content = terminal_width - 3
            line = line[:max_content] + "..."

        print(line)


def cast_columns_to_category(df, columns, inplace=False):
    """
    Cast specified columns to category dtype.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    columns : str or list of str
        Column name(s) to convert to category
    inplace : bool, default False
        If True, modify DataFrame in-place and return None

    Returns
    -------
    pd.DataFrame or None
        DataFrame copy with specified columns as category dtype, or None if inplace=True

    Raises
    ------
    KeyError
        If any specified columns don't exist in DataFrame
    """
    # handle single column as string
    if isinstance(columns, str):
        columns = [columns]

    # validate columns exist
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Columns not found in DataFrame: {missing_cols}")

    df = df if inplace else df.copy()
    df[columns] = df[columns].astype("category")
    return None if inplace else df
