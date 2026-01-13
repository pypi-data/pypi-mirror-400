# Datamazing

The Datamazing package provides an interface for various transformations of data (filtering, aggregation, merging, etc.)

## Interface

The interface is very similar to those of most DataFrame libraries (pandas, pyspark, SQL, etc.). For example, a group-by is implemented as `group(df, by=["..."])`, and a merge is implemented as `merge([df1, df2], on=["..."], how="inner")`. So, why not just use native pandas, pyspark, etc.?

1. The native libraries have some parts, with a little annoying interface (such as pandas inconsistent use of indexing)
2. Ability to add custom operations, used specifically for the Energinet domain.

## Backends

The package contains methods with the same interface, but for different backends. Currently, 2 backends are supported: `pandas` and `pyspark` (though not all methods are available for both). For example, when working with `pandas` DataFrames, one would use

```python
import pandas as pd
import datamazing.pandas as pdz

df = pd.DataFrame([
    {"animal": "cat", "time": pd.Timestamp("2020-01-01"), "age": 1.0},
    {"animal": "cat", "time": pd.Timestamp("2020-01-02"), "age": 3.0},
    {"animal": "dog", "time": pd.Timestamp("2020-01-01"), "age": 5.0},
])

pdz.group(df, by="animal") \
    .resample(on="time", resolution=pd.Timedelta(hours=12)) \ 
    .agg("interpolate")
```
whereas, when working with `pyspark` DataFrame, one would instead use

```python
import datetime as dt
import pyspark.sql as ps
import datamazing.pyspark as psz

spark = ps.SparkSession.getActiveSession()

df = spark.createDataFrame([
    {"animal": "cat", "time": dt.datetime(2020, 1, 1), "age": 1.0},
    {"animal": "cat", "time": dt.datetime(2020, 1, 2), "age": 3.0},
    {"animal": "dog", "time": dt.datetime(2020, 1, 1), "age": 5.0},
])

psz.group(df, by="animal") \
    .resample(on="time", resolution=pd.Timedelta(hours=12)) \ 
    .agg("interpolate")
```

## Development

To setup the Python environment, run

```bash
$ pip install poetry
$ poetry install
```

To run test locally one needs java. This can be installed using the following:
```bash
$ sudo apt install default-jdk
```

To execute unit tests, run

```bash
$ pytest .
```