import pandas as pd
import pyspark.sql.functions as f
from pyspark.sql.types import FloatType, TimestampType


def time_between(t1: TimestampType, t2: TimestampType, unit: pd.Timedelta) -> FloatType:
    seconds = unit.total_seconds()
    return f.try_subtract(t2, t1).cast("long").cast("double") / seconds


def floor_time(t: TimestampType, nearest: pd.Timedelta) -> TimestampType:
    seconds = nearest.total_seconds()
    return f.from_unixtime(f.floor(f.unix_timestamp(t) / seconds) * seconds).cast(
        "timestamp"
    )


def ceil_time(t: TimestampType, nearest: pd.Timedelta) -> TimestampType:
    seconds = nearest.total_seconds()
    return f.from_unixtime(f.ceil(f.unix_timestamp(t) / seconds) * seconds).cast(
        "timestamp"
    )
