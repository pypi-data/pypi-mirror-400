import typing

import pandas as pd
import pyspark.sql as ps

import datamazing.pandas as pdz
from datamazing.pandas.datacollection import TimeInterval
from datamazing.pandas.testing.data import get_filepath  # noqa: F401


def make_df(data: list[dict]):
    spark = ps.SparkSession.getActiveSession()
    pdf = pdz.testing.make_df(data)
    return spark.createDataFrame(pdf)


def read_df(
    filename: str,
    subfolder: str = "data",
) -> ps.DataFrame:
    """
    Read pyspark DataFrame from test data.
    Datetimes and timedeltas are inferred automatically.

    Args:
        filename (str): Name of CSV file with test data
        subfolder (str, optional): Subfolder relative to test being
            run currently (taken from  the environment variable PYTEST_CURRENT_TEST),
            from where to read the test data. Defaults to "data".

    Example:
    >>> read_df(filename="data.df.csv")
    """
    spark = ps.SparkSession.getActiveSession()

    pdf = pdz.testing.read_df(filename, subfolder)
    return spark.createDataFrame(pdf)


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
        self.pdb = pdz.testing.TestDatabase(file_pattern, subfolder, time_column)

    def query(
        self, table_name: str, time_interval: typing.Optional[TimeInterval] = None
    ) -> pd.DataFrame:
        spark = ps.SparkSession.getActiveSession()

        pdf = self.pdb.query(table_name, time_interval)
        return spark.createDataFrame(pdf)
