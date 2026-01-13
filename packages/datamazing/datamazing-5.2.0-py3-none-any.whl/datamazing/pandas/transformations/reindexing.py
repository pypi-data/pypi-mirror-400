import pandas as pd


class Reindexer:
    def __init__(
        self,
        df: pd.DataFrame,
        on: str,
        at: pd.Series | pd.Timestamp,
    ):
        self.df = df
        self.on = on
        self.at = at

    def interpolate(self, method: str = "linear"):
        """Interpolate time series.
        For example, if the input is a time series D with
        daily resolution, then we can interpolate, using
        a linear function, to another set of timestamps,
        and produce a new time series T. In other words:

            - Input:    D(day)
            - Output:   T(t) = interpolate(t between day+0 and day+1)

        Args:
            method (str): Interpolation method ("linear", "ffill" or "bfill")
        """
        # interpolating at a single point
        # should return a Series, instead
        # of a DataFrame
        if isinstance(self.at, pd.Timestamp):
            single_point = True
        else:
            single_point = False

        self.at = pd.Series(self.at)

        # only allow certain interpolation methods
        # to avoid untested behavior
        supported_methods = ["linear", "ffill", "bfill"]
        if method not in supported_methods:
            raise ValueError(f"Method must be one of {supported_methods}")

        # in pandas, the interpolation method `linear`
        # ignores the time values. We need to use `time`
        if method == "linear":
            method = "time"

        # pandas doesn't handle empty dataframes very well
        if self.df.empty:
            return self.df

        df = self.df.sort_values(by=self.on)

        union_index = pd.concat([self.at, df[self.on]]).drop_duplicates().sort_values()

        df = (
            df.set_index(self.on)
            .reindex(union_index)
            .interpolate(method)
            .reindex(self.at)
            .rename_axis(self.on)
            .reset_index()
        )

        if single_point:
            s = df.iloc[0]
            s.name = None
            return s

        return df


def reindex(df: pd.DataFrame, on: str, at: pd.Series | pd.Timestamp):
    return Reindexer(df, on, at)
