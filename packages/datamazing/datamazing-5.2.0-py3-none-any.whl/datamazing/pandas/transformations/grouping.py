import typing

import pandas as pd

from datamazing._conform import _concat, _list
from datamazing.pandas.transformations import resampling


class GrouperResampler:
    def __init__(
        self,
        gb: "Grouper",
        on: str,
        resolution: pd.Timedelta,
    ):
        self.gb = gb
        self.on = on
        self.resolution = resolution

    def agg(self, method: str | dict, edge: str = "left"):
        """Aggregate (downsample) time series.
        For example, if the input is a time series H with
        hourly resolution, then we can aggregate, using
        the mean, to daily resolution, and produce a new
        time series D. In other words:

            - Input:    H(hour)
            - Output:   D(day) = mean( H(hour) for hour in day)

        Args:
            method (str | dict): Name of method (e.g. "sum") or
                dictionary of method(s) to use for each column
                (e.g. {"col1": "mean", "col2": ["min", "max"]})
            edge (str, optional): Which side of the interval
                to use as label ("left" or "right").
                Defaults to "left".
        """
        df = (
            self.gb.df.sort_values(by=self.on)
            .set_index(self.on)
            .groupby(self.gb.by, dropna=False, observed=True)
            .resample(rule=self.resolution, closed=edge, label=edge)
            .aggregate(method, numeric_only=True)
        )

        # depending on the resampling aggregation
        # method, pandas will include the group-by
        # columns in both the index and the columns
        df = df.drop(columns=self.gb.by, errors="ignore")

        df = df.reset_index()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ["_".join(col).strip("_") for col in df.columns]

        return df

    def interpolate(self, method: str = "linear"):
        """Interpolate (upsample) time series.
        For example, if the input is a time series D with
        daily resolution, then we can interpolate, using
        a linear function, to hourly resolution, and
        produce a new time series H. In other words:

            - Input:    D(day)
            - Output:   H(hour) = interpolate(hour between day+0 and day+1)

        Args:
            method (str): Interpolation method ("linear", "ffill" or "bfill")

        Raises:
            ValueError: Currently, interpolation can only be done
                when the original time series has a resolution
                which is an integer factor of the upsample resolution.
                Thus, one can go from 1 hour-resolution to 5 minute
                -resolution, but not the other way around. This
                restriction is purely a pandas issue, and can be
                fixed if desired.
        """
        # only allow certain interpolation methods
        # to avoid untested behavior
        supported_methods = ["linear", "ffill", "bfill"]
        if method not in supported_methods:
            raise ValueError(f"Method must be one of {supported_methods}")

        # in pandas, the aggregation method `linear`
        # doesn't exist. We need to use `interpolate`
        if method == "linear":
            method = "interpolate"

        df = self.gb.df.sort_values(by=self.on)

        diff_factors = (
            df.groupby(self.gb.by, observed=True)[self.on].diff().dropna()
            / self.resolution
        )

        if ((diff_factors % 1) != 0).any():
            raise ValueError(
                f"Interpolation only possible "
                f"when the original time resolution "
                f"is an integer factor of the upsample "
                f"resolution '{self.resolution}'."
            )

        start_time = df[self.on].min()
        end_time = df[self.on].max()

        df = (
            df.set_index(self.on)
            .groupby(self.gb.by, dropna=False, observed=True)
            .resample(rule=self.resolution)
            .aggregate(method)
        )

        # depending on the resampling aggregation
        # method, pandas will include the group-by
        # columns in both the index and the columns
        df = df.drop(columns=self.gb.by, errors="ignore")

        df = df.reset_index()

        # after resampling, pandas might leave
        # timestamps outside of the original interval
        if not df.empty:
            df = df[df[self.on].between(start_time, end_time)]

        return df

    def granulate(self, block_size: pd.Timedelta, edge: str = "left"):
        """Fine-grain (upsample) time series.
        For example, if the input is a time series D with
        daily resolution, then we can granulate to hourly
        resolution, and produce a new time series H.
        In other words:

            - Input:    D(day)
            - Output:   H(hour) = D(day containing hour)


        Args:
            block_size: The block size in which the time is granulated.
            edge (str, optional): Which side of the interval
                to use as label ("left" or "right").
                Defaults to "left".
        """
        # pandas doesn't handle empty dataframes very well
        if self.gb.df.empty:
            return self.gb.df

        df = self.gb.df.groupby(
            self.gb.by, dropna=False, group_keys=False, observed=True
        ).apply(
            lambda group: resampling.resample(
                group, self.on, self.resolution
            ).granulate(block_size, edge)
        )

        return df


class Grouper:
    def __init__(self, df: pd.DataFrame, by: list[str]):
        self.df = df
        self.by = by

    def agg(self, method: str | dict):
        """Aggregate table.

        Args:
            method (str | dict): Name of method (e.g. "sum") or
                dictionary of method(s) to use for each column
                (e.g. {"col1": "mean", "col2": ["min", "max"]})
        """
        if self.df.empty:
            aggregate_options = {}
        elif method in ["sum", "mean", "std", "var"]:
            aggregate_options = {"numeric_only": "True"}
        else:
            aggregate_options = {}
        df = (
            self.df.set_index(self.by)
            .groupby(self.by, dropna=False, observed=True)
            .aggregate(method, **aggregate_options)
            .reset_index()
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ["_".join(col).strip("_") for col in df.columns]

        return df

    def resample(self, on: str, resolution: pd.Timedelta):
        return GrouperResampler(self, on, resolution)

    def pivot(self, on: list[str], values: typing.Optional[list[tuple[str]]] = None):
        """
        Pivot table. Non-existing combinations will be filled
        with NaNs.

        Args:
            on (list[str]): Columns which to pivot
            values (list[tuple[str]], optional): Enforce
                the existence of columns with these names
                after pivoting. Defaults to None, in which
                case the values will be inferred from the
                pivoting column.
        """

        df = self.df.set_index(_concat(self.by, on))

        if values:
            by_vals = df.index.to_frame(index=False)[_list(self.by)].drop_duplicates()
            on_vals = pd.DataFrame(values, columns=_list(on))
            cross_vals = by_vals.merge(on_vals, how="cross")
            df = df.reindex(pd.MultiIndex.from_frame(cross_vals))

        df = df.unstack(on)

        # concatenate multiindex columns to single index columns
        concat_cols = []
        suffix = len(df.columns.levels[0]) > 1
        for col in df.columns:
            concat_col = "_".join([str(item) for item in col[1:]])
            if suffix:
                # if more than one remaning columns, suffix with that
                concat_col = concat_col + "_" + str(col[0])
            concat_col = concat_col.strip("_")
            concat_cols.append(concat_col)
        df.columns = concat_cols

        return df.reset_index()

    def latest(self, on: str):
        return (
            self.df.set_index(_concat(self.by, on))
            .sort_index(level=on)
            .groupby(self.by, dropna=False, observed=True)
            .tail(1)
            .reset_index()
        )

    def earliest(self, on: str):
        return (
            self.df.set_index(_concat(self.by, on))
            .sort_index(level=on)
            .groupby(self.by, dropna=False, observed=True)
            .head(1)
            .reset_index()
        )


def group(df: pd.DataFrame, by: list[str]):
    return Grouper(df, by)
