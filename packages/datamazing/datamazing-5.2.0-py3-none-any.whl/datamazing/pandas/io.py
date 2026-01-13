from os import PathLike

import pandas as pd

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
ISO_FORMAT_MILLISECONDS = "%Y-%m-%dT%H:%M:%S.%f%z"


def infer_iso_datetime(values: pd.Series) -> pd.Series:
    try:
        converted_values = pd.to_datetime(values, format=ISO_FORMAT_MILLISECONDS)
    except (ValueError, TypeError):
        try:
            converted_values = pd.to_datetime(values, format=ISO_FORMAT)
        except (ValueError, TypeError):
            # if not possible to parse as datetime, return original values
            return values
    return converted_values


def infer_iso_timedelta(values: pd.Series) -> pd.Series:
    try:
        converted_values = pd.to_timedelta(values)
    except (ValueError, TypeError):
        # if not possible to parse as time delta, return original values
        return values
    try:
        values_isoformat = converted_values.apply(pd.Timedelta.isoformat)
    except (TypeError, AttributeError):
        return values
    if not (values_isoformat == values).all():
        # if original values is not in ISO 8601 format, return original values
        return values
    return converted_values


def read_csv(filepath: PathLike) -> pd.DataFrame:
    """
    Read CSV into DataFrame. All types are inferred.
    Datetimes and timedeltas in ISO 8601 format are inferred automatically.

    One can specify the type in the column name instead of relying on the inferred type.
    This is done using the following syntax: <column_name>:<type>.

    Some conversions are invalid and the will cause the reading to fail.
    Example of invalid conversions:
    - converting a string to a float

    Args:
        filepath (str): Filepath of the CSV file
    """
    df = pd.read_csv(filepath, keep_default_na=False, na_values=["nan"])

    # Auto cast types based on type hint in column name
    # type hints are on the form <column_name>:<type_hint>
    renames = {}
    for column_name in df.columns:
        if ":" in column_name:
            name, type_hint = column_name.split(":")
            df[column_name] = df[column_name].astype(type_hint)
            renames[column_name] = name
        else:
            # try converting ISO 8601 strings to pd.Timestamp and pd.Timedelta
            df[column_name] = infer_iso_datetime(df[column_name])
            df[column_name] = infer_iso_timedelta(df[column_name])

    df = df.rename(columns=renames)

    # convert all nan strings to None
    df = df.where(df != "nan", None)

    return df
