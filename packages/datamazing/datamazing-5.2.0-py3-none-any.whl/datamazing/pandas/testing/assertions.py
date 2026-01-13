import pandas as pd


def assert_frame_equal(
    left: pd.DataFrame,
    right: pd.DataFrame,
    check_order: bool = False,
):
    if check_order:
        pd.testing.assert_frame_equal(left, right)
    else:
        columns = list(left.columns)
        pd.testing.assert_frame_equal(
            left=left.sort_values(by=columns).reset_index(drop=True),
            right=right.sort_values(by=columns).reset_index(drop=True),
            check_like=True,
        )


def assert_series_equal(
    left: pd.Series,
    right: pd.Series,
    check_order: bool = False,
):
    if check_order:
        pd.testing.assert_series_equal(left, right)
    else:
        pd.testing.assert_series_equal(
            left.sort_index(),
            right.sort_index(),
        )
