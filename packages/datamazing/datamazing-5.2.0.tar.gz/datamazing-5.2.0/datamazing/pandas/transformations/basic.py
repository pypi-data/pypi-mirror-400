from functools import reduce

import numpy as np
import pandas as pd

# we dont use pd.Timestamp.min and pd.Timestamp.max,
# as these values are too obscure
MIN_TIMESTAMP = pd.Timestamp("1900-01-01T00:00:00")
MAX_TIMESTAMP = pd.Timestamp("2200-01-01T00:00:00")


def fill_empty_periods(df, period: tuple[str, str]):
    df = df.copy()
    min_timestamp = MIN_TIMESTAMP.tz_localize(getattr(df.dtypes[period[0]], "tz", None))
    max_timestamp = MAX_TIMESTAMP.tz_localize(getattr(df.dtypes[period[1]], "tz", None))
    df[period[0]] = df[period[0]].fillna(min_timestamp)
    df[period[1]] = df[period[1]].fillna(max_timestamp)
    return df


def latest(
    df: pd.DataFrame,
    on: str,
):
    s = df.sort_values(by=on).iloc[-1]
    s.name = None
    return s


def earliest(df: pd.DataFrame, on: str):
    s = df.sort_values(by=on).iloc[0]
    s.name = None
    return s


def as_of_time(
    df: pd.DataFrame,
    period: tuple[str, str],
    at: pd.Timestamp,
    closed: str = "left",
):
    """Get snapshot of periodized DataFrame
    at a specified timestamp

    Args:
        df (pd.DataFrame): DataFrame
        period (tuple[str, str]): Periodization columns (valid-from, valid-to)
        at (pd.Timestamp): Timestamp to get snapshot at
        closed (str, optional): Boundary of periodization intervals. Defaults to "left".
    """
    df = fill_empty_periods(df, period)

    return df[
        pd.IntervalIndex.from_arrays(
            df[period[0]], df[period[1]], closed=closed
        ).contains(at)
    ]


def shift_time(
    df: pd.DataFrame,
    on: str,
    period: pd.Timedelta,
):
    df = df.copy()
    df[on] = df[on] + period
    return df


def unique_one(s: pd.Series) -> object:
    if len(s.unique()) > 1:
        raise ValueError("Series has more than one unique value")
    return s.iloc[0]


def concat_by_name(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    columns = [df.columns for df in dfs]
    common_cols = reduce(lambda cols1, cols2: cols1.union(cols2), columns).unique()
    return pd.concat([df.reindex(columns=common_cols) for df in dfs], ignore_index=True)


def unpivot(
    df: pd.DataFrame, on: list[str], variable: str = "variable", value: str = "value"
):
    remaining_cols = df.columns.drop(on).tolist()
    df = df.set_index(remaining_cols)
    df.columns.name = variable
    s = df.stack()
    s.name = value
    df = s.reset_index()
    return df


def switch(
    cases: list[tuple[pd.Series, pd.Series | object]],
    default: pd.Series | object,
) -> pd.Series:
    """Choose among a set of values depending on a set of conditions

    Args:
        cases (list[tuple[pd.Series, pd.Series  |  object]]):
            List of cases, with each element being a tuple
            of the form (when, then). I.e. if `when` is satisfied,
            choose `then`. If multiple cases are satisfied,
            the first one is choosen.
        default (pd.Series | object):
            If no cases are satisfied, this value will be choosen.

    Example:
    >>> df["sign"] = pdz.switch(
    ...     cases=[
    ...         (df["value"] > 0, "positive"),
    ...         (df["value"] < 0, "negative"),
    ...     ],
    ...     default="zero",
    ... )
    """
    array = np.select(
        condlist=[case[0] for case in cases],
        choicelist=[case[1] for case in cases],
        default=default,
    )

    return pd.Series(array)
