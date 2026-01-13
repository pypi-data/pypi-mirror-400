import typing

import pandas as pd
import pyspark.sql as ps
import pyspark.sql.functions as f
from pyspark.sql.functions import date_format

from datamazing._conform import _concat, _list


class GrouperResampler:
    def __init__(
        self,
        gb: "Grouper",
        on: str,
        resolution: pd.Timedelta,
        edge: str,
    ):
        self.gb = gb
        self.on = on
        self.resolution = resolution
        self.edge = edge

    def agg(self, method: str):
        if self.edge == "right":
            round_func = f.ceil
        elif self.edge == "left":
            round_func = f.floor
        else:
            raise ValueError(f"Unsupported value {self.edge} for `edge`")

        resolution_sec = self.resolution.total_seconds()
        rounded_time = (
            round_func(f.unix_timestamp(self.on) / resolution_sec) * resolution_sec
        ).cast("timestamp")

        df = self.gb.df.withColumn(
            "__rounded_time", date_format(rounded_time, "yyyy-MM-dd HH:mm:ss")
        ).drop(self.on)

        df = group(df, by=_concat(self.gb.by, "__rounded_time")).agg(method)

        df = df.withColumn(self.on, f.col("__rounded_time").cast("timestamp"))

        df = df.drop("__rounded_time")

        return df


class Grouper:
    def __init__(self, df: ps.DataFrame, by: list[str]):
        self.df = df
        self.by = by

    def agg(self, method: str):
        remaining = set(self.df.columns).difference(_list(self.by))
        agg_func = getattr(f, method)

        return self.df.groupBy(self.by).agg(
            *[agg_func(col).alias(col) for col in remaining]
        )

    def latest(self, on: str):
        version_window = ps.Window.partitionBy(self.by).orderBy(f.desc(on))
        return (
            self.df.withColumn("__version", f.row_number().over(version_window))
            .filter(f.col("__version") == 1)
            .drop("__version")
        )

    def earliest(self, on: str):
        version_window = ps.Window.partitionBy(self.by).orderBy(f.asc(on))
        return (
            self.df.withColumn("__version", f.row_number().over(version_window))
            .filter(f.col("__version") == 1)
            .drop("__version")
        )

    def resample(self, on: str, resolution: pd.Timedelta, edge: str = "left"):
        return GrouperResampler(self, on, resolution, edge)

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
        if values:
            # if values is a list of tuples, concatenate these
            # so that they match the resulting pivoted columns
            values = [
                "_".join([str(item) for item in _list(value)]) for value in values
            ]

        remaining = set(self.df.columns).difference(_list(on), _list(self.by))

        df = (
            self.df.withColumn("__on", f.concat_ws("_", *_list(on)))
            .groupBy(self.by)
            .pivot("__on", values=values)
            .agg(*[f.first(col).alias(col) for col in remaining])
        )

        return df


def group(df: ps.DataFrame, by: list[str]):
    return Grouper(df, by)
