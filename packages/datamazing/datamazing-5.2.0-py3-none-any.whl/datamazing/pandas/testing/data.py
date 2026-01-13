import os
import typing
from pathlib import Path

import pandas as pd

from datamazing.pandas import io
from datamazing.pandas.types import TimeInterval


def get_filepath(filename: str, subfolder: str = "data"):
    return Path(os.environ["PYTEST_CURRENT_TEST"]).parent / subfolder / filename


def make_df(data: list[dict]):
    return pd.DataFrame.from_records(data)


def make_series(data: dict):
    return pd.Series(data)


def read_df(filename: str, subfolder: str = "data") -> pd.DataFrame:
    """
    Read pandas DataFrame from test data.
    Datetimes and timedeltas are inferred automatically.

    Args:
        filename (str): Name of CSV file with test data
        subfolder (str, optional): Subfolder relative to test being
            run currently (taken from  the environment variable PYTEST_CURRENT_TEST),
            from where to read the test data. Defaults to "data".

    Example:
    >>> read_df(filename="data.df.csv")
    """
    filepath = get_filepath(filename, subfolder)
    df = io.read_csv(filepath)

    return df


class TestDatabase:
    def __init__(
        self, file_pattern: str, subfolder: str = "data", time_column: str = "time_utc"
    ):
        """Read Database from test data.
        Datetimes and timedeltas are inferred automatically.

        Args:
            file_pattern (str): Pattern of CSV files with test data
                using placeholder `{table_name}`
            subfolder (str, optional): Subfolder relative to test being
                run currently (taken from  the environment variable
                PYTEST_CURRENT_TEST), from where to read the test data.
                Defaults to "data".

        Example:
        >>> TestData(file_pattern="{table_name}.df.csv")
        """
        self.file_pattern = file_pattern
        self.subfolder = subfolder
        self.time_column = time_column

    def query(
        self,
        table_name: str,
        time_interval: typing.Optional[TimeInterval] = None,
        filters: typing.Optional[dict[str, object]] = None,
    ) -> pd.DataFrame:
        # get filename associated with table
        filename = self.file_pattern.format(table_name=table_name)

        df = read_df(filename, subfolder=self.subfolder)

        if time_interval:
            # filter to time interval
            is_after_start = df[self.time_column] >= time_interval.left
            is_before_end = df[self.time_column] <= time_interval.right
            is_in_interval = is_after_start & is_before_end
            df = df[is_in_interval]

        if filters:
            for key, value in filters.items():
                if key not in df.columns:
                    raise KeyError(f"The column {key} is not found in {table_name}.")
                if not isinstance(value, list):
                    value = [value]
                df = df[df[key].isin(value)]

            df = df.reset_index(drop=True)

        return df
