from dataclasses import dataclass

import pandas as pd
from pandas.tseries.offsets import DateOffset


@dataclass
class TimeInterval:
    """
    Class representing a time interval

    Args:
        left (pd.Timestamp): Left end of interval
        right (pd.Timestamp): Right end of interval
    """

    left: pd.Timestamp
    right: pd.Timestamp

    def __post_init__(self):
        self.left = pd.Timestamp(self.left)
        self.right = pd.Timestamp(self.right)

    def shift(self, period: pd.Timedelta) -> "TimeInterval":
        return TimeInterval(
            left=self.left + period,
            right=self.right + period,
        )

    def to_range(self, freq: pd.Timedelta, name: str = "time_utc") -> pd.DatetimeIndex:
        return pd.date_range(self.left, self.right, freq=freq, name=name)

    def isoformat(self) -> str:
        return f"{self.left.isoformat()}/{self.right.isoformat()}"

    def tz_localize(self, tz: str) -> "TimeInterval":
        """Localize a TimeInterval to a timezone.

        Args:
            tz (str): The timezone to localize to.

        Returns:
            TimeInterval: The localized TimeInterval.
        """
        return TimeInterval(
            left=self.left.tz_localize(tz),
            right=self.right.tz_localize(tz),
        )

    def tz_convert(self, tz: str) -> "TimeInterval":
        """Convert a TimeInterval to a different timezone.

        Args:
            tz (str): The timezone to convert to.

        Returns:
            TimeInterval: The converted TimeInterval.
        """
        return TimeInterval(
            left=self.left.tz_convert(tz),
            right=self.right.tz_convert(tz),
        )

    @classmethod
    def from_date(cls, date: pd.Timestamp) -> "TimeInterval":
        """Create a TimeInterval from a date. The TimeInterval covers the whole day.
        Can be used to create a TimeInterval for a Danish day.

        Example:
        ```python
        date = pd.Timestamp.utcnow()
        date_cet = date.tz_convert("Europe/Copenhagen")
        time_interval_danish_day_cet = TimeInterval.from_date(date_cet)
        time_interval_danish_day_utc = time_interval_danish_day_cet.tz_convert("UTC")

        >>> time_interval_danish_day_utc
        TimeInterval(
            left=Timestamp('2024-09-26 22:00:00+0000', tz='UTC'),
            right=Timestamp('2024-09-27 22:00:00+0000', tz='UTC')
        )
        ```

        Args:
            date (pd.Timestamp): The date to change to a TimeInterval

        Returns:
            TimeInterval: The TimeInterval from start of day to start of next day
        """
        whole_date = date.floor("D")
        left = whole_date
        right = whole_date + DateOffset(days=1)
        return cls(
            left=left,
            right=right,
        )

    @classmethod
    def fromisoformat(cls, string: str) -> "TimeInterval":
        start, end = string.split("/")
        return cls(
            left=pd.Timestamp(start),
            right=pd.Timestamp(end),
        )

    def __hash__(self):
        return hash((self.left, self.right))
