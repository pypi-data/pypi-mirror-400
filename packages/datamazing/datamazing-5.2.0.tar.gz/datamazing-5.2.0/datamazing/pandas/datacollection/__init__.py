from abc import ABC, abstractmethod

import pandas as pd

from datamazing.pandas.types import TimeInterval


class Database(ABC):
    @abstractmethod
    def query(
        self, table_name: str, time_interval: TimeInterval, filters: dict[str, object]
    ) -> pd.DataFrame:
        raise NotImplementedError
