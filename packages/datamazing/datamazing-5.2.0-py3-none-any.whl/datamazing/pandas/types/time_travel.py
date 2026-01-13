from dataclasses import dataclass, field

import pandas as pd


@dataclass
class TimeTravel:
    """
    Class representing a time travel either
    - absolute: How did data look for time T at a point in time T0
    - relative: How did data look for time T at a horizon of H prior
        to the time block B containing T.

    Example:
    Consider a versioned time series (slowly changing dimension, type 2) with
    columns `time`, `value`, `valid_from` and `valid_to`. Time travelling
    absolutely to the point in time T0, means considering the time series
    where `valid_from <= T0 < valid_to`. Time travelling to relatively with
    horizon H and block B, menas consider the time series where
    `valid_from <= floor(time_utc, block) - horizon < valid_to`.

    Args:
        [absolute time travel]
            as_of_time (pd.Timestamp): Point in time to time travel to.
        [relative time travel]
            horizon (pd.Timedelta): Period to look into future.
            block (pd.Timedelta): Period used to partition the
                timeline into discrete blocks. The horizon
                will be relative to the start of each block.
    """

    as_of_time: pd.Timestamp = None
    horizon: pd.Timedelta = None
    block: pd.Timedelta = None
    tense: str = field(init=False)

    def __post_init__(self):
        if self.as_of_time is not None and (
            self.horizon is not None or self.block is not None
        ):
            raise ValueError(
                "Can only specify one of `as_of_time` and `horizon`/`block`"
            )

        if self.as_of_time is None and (self.horizon is None or self.block is None):
            raise ValueError("Must specify one of `as_of_time` and `horizon`/`block`")

        if self.as_of_time is not None:
            self.tense = "absolute"
        else:
            self.tense = "relative"

    def __hash__(self):
        return hash((self.as_of_time, self.horizon, self.block))
