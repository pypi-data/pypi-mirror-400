import pyspark.sql as ps

import datamazing.pandas as pdz


def assert_frame_equal(
    left: ps.DataFrame, right: ps.DataFrame, check_order: bool = False
):
    pdz.testing.assert_frame_equal(
        left=left.toPandas(),
        right=right.toPandas(),
        check_order=check_order,
    )
