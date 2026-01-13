import pandas as pd

ZERO_INTERVAL = pd.Timedelta(microseconds=0)


class Resampler:
    def __init__(
        self,
        df: pd.DataFrame,
        on: str,
        resolution: pd.Timedelta,
    ):
        self.df = df
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
            self.df.sort_values(by=self.on)
            .set_index(keys=self.on)
            .resample(rule=self.resolution, label=edge, closed=edge)
            .aggregate(method, numeric_only=True)
            .reset_index()
        )

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ["_".join(col).strip("_") for col in df.columns]

        return df

    def interpolate(
        self,
        method: str = "linear",
        order=None,
    ):
        """Interpolate (upsample) time series.
        For example, if the input is a time series D with
        daily resolution, then we can interpolate, using
        a linear function, to hourly resolution, and
        produce a new time series H. In other words:

            - Input:    D(day)
            - Output:   H(hour) = interpolate(hour between day+0 and day+1)

        Args:
            method (str): Interpolation method. Must be one of
                'linear'
                'ffill'
                'bfill'
                'nearest'
                'zero'
                'slinear'
                'quadratic'
                'cubic'
                'barycentric'
                'polynomial'
                'krogh'
                'piecewise_polynomial'
                'spline'
                'pchip'
                'akima'
                'cubicspline'

            order (int): Order of interpolation method when using one of
                'polynomial'
                'spline'

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
        supported_methods = [
            "linear",
            "ffill",
            "bfill",
            "nearest",
            "zero",
            "slinear",
            "quadratic",
            "cubic",
            "barycentric",
            "polynomial",
            "krogh",
            "piecewise_polynomial",
            "spline",
            "pchip",
            "akima",
            "cubicspline",
        ]
        if method not in supported_methods:
            raise ValueError(f"Method must be one of {supported_methods}")

        # in pandas, the interpolation method `linear`
        # assumes that the timestamps are evenly spaced.
        # This might no be the case when reindexing, so
        # instead we can use the method `time`
        if method == "linear":
            method = "time"

        # pandas doesn't handle empty dataframes very well
        if self.df.empty:
            return self.df

        df = self.df.sort_values(by=self.on)

        diff_factors = df[self.on].diff().dropna() / self.resolution

        if ((diff_factors % 1) != 0).any():
            raise ValueError(
                f"Interpolation only possible "
                f"when the original time resolution "
                f"is an integer factor of the upsample "
                f"resolution '{self.resolution}'."
            )

        start_time = df[self.on].min()
        end_time = df[self.on].max()

        # use correct limit direction
        if method in ["bfill", "backfill"]:
            limit_direction = "backward"
        elif method in ["pad", "ffill"]:
            limit_direction = "forward"
        else:
            limit_direction = None

        if order:
            interpolation_options = {"order": order}
        else:
            interpolation_options = {}

        df = (
            df.set_index(self.on)
            .resample(rule=self.resolution)
            .interpolate(
                method, limit_direction=limit_direction, **interpolation_options
            )
            .reset_index()
        )

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
        if self.df.empty:
            return self.df

        df = self.df.sort_values(by=self.on)

        if edge == "left":
            left_margin = ZERO_INTERVAL
            right_margin = block_size
        elif edge == "right":
            left_margin = -block_size
            right_margin = ZERO_INTERVAL
        else:
            raise ValueError(f"Unsupported value {edge} for `edge`")

        df[self.on] = df.apply(
            lambda row: pd.date_range(
                row[self.on] + left_margin,
                row[self.on] + right_margin,
                freq=self.resolution,
                inclusive=edge,
            ),
            axis="columns",
        )

        df = df.explode(column=self.on).reset_index(drop=True)

        return df


def resample(df: pd.DataFrame, on: str, resolution: pd.Timedelta):
    return Resampler(df, on, resolution)
