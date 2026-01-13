from functools import reduce

import pandas as pd

from datamazing._conform import _concat
from datamazing.pandas.transformations import basic


def merge_many(
    dfs: list[pd.DataFrame],
    on: list[str],
    how: str = "inner",
) -> pd.DataFrame:
    return reduce(lambda df1, df2: df1.merge(df2, on=on, how=how), dfs)


def merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_on: list[str] | None = None,
    right_on: list[str] | None = None,
    on: list[str] | None = None,
    left_time: str | None = None,
    right_period: tuple[str, str] | None = None,
    how: str = "inner",
    suffixes: tuple[str, str] = ("_x", "_y"),
):
    if on:
        if left_on is not None or right_on is not None:
            # raise same error as pd.merge
            raise pd.errors.MergeError(
                'Can only pass argument "on" OR "left_on" '
                'and "right_on", not a combination of both.'
            )
        left_on = on
        right_on = on

    if bool(left_time) != bool(right_period):
        raise ValueError(
            "Both `left_time` and `right_period` must be set when time-merging"
        )

    if left_time and right_period:
        if how not in ["inner", "left"]:
            raise ValueError(
                'Only "inner" or "left" join is supported when time-merging'
            )

        # sort values in order to use `pd.merge_asof`
        left = left.sort_values(by=left_time)

        right = basic.fill_empty_periods(df=right, period=right_period)
        right = right.sort_values(by=right_period[0])

        # make left-join, matching the latest right-start-time
        # which is below the left-time
        df = pd.merge_asof(
            left,
            right,
            left_on=left_time,
            right_on=right_period[0],
            left_by=left_on,
            right_by=right_on,
            suffixes=suffixes,
        )

        # remove matches, where the right-end-time is also below the left-time.
        df = df[df[left_time] < df[right_period[1]]]

        # the above code, actually does an inner-join, so we need to
        # add the remaining rows from the left dataframe.
        # we need to take into account overlapping columns,
        # which needs to be appended with the given suffixes
        if how == "left":
            df_right_cols = df.filter(
                list(right.columns) + list(right.columns + suffixes[1]) + [left_time]
            )

            df_right_cols.columns = df_right_cols.columns.str.replace(suffixes[1], "")

            # pandas has improved merge performance in 3, but we can
            # enable it for pandas 2 using mode.copy_on_write option
            with pd.option_context("mode.copy_on_write", True):
                df = pd.merge(
                    left,
                    df_right_cols,
                    left_on=_concat(left_on, left_time),
                    right_on=_concat(right_on, left_time),
                    how="left",
                    suffixes=suffixes,
                )

    else:
        # pandas has improved merge performance in 3, but we can
        # enable it for pandas 2 using mode.copy_on_write option
        with pd.option_context("mode.copy_on_write", True):
            df = pd.merge(
                left,
                right,
                left_on=left_on,
                right_on=right_on,
                how=how,
                suffixes=suffixes,
            )

    return df


def align(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_on: list[str] | None = None,
    right_on: list[str] | None = None,
    on: list[str] | None = None,
    how: str = "inner",
):
    if on:
        if left_on is not None or right_on is not None:
            # raise same error as pd.merge
            raise pd.errors.MergeError(
                'Can only pass argument "on" OR "left_on" '
                'and "right_on", not a combination of both.'
            )
        left_on = on
        right_on = on

    left = left.set_index(left_on)
    right = right.set_index(right_on)

    aligned_left, aligned_right = left.align(right, join=how, axis="index")

    aligned_left = aligned_left.reset_index()
    aligned_right = aligned_right.reset_index()

    return aligned_left, aligned_right
