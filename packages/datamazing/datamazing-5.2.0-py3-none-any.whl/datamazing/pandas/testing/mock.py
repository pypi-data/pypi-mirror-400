from unittest import mock

import pandas as pd


def patch_utcnow(timestamp: pd.Timestamp):
    return mock.patch("pandas.Timestamp.utcnow", new=lambda: timestamp)
