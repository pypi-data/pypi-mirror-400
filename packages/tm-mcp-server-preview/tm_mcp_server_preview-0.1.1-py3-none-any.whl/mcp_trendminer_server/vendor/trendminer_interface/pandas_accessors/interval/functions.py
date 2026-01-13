import pandas as pd
import random
import trendminer_interface._input as ip
from trendminer_interface.constants import CALCULATION_OPTIONS


def sample(interval, duration, n, overlap, freq, name):
    """Sample random sub-intervals from the current interval

    Parameters
    ----------
    interval : pandas.Interval
        Interval to sample
    duration : pandas.Timedelta
        Duration of the sample intervals
    n : int
        Number of intervals to return
    overlap : bool
        Whether the returned sample intervals can overlap
    freq : pandas.Timedelta
        The resolution to which all inputs and outputs will be rounded. Defaults to your index resolution.
    name : str
        Index name

    Returns
    -------
    IntervalIndex
    """

    relative_duration = duration/freq

    if overlap:
        max_value = int((interval.length - duration)/freq)
        values = [random.randint(0, max_value) for _ in range(n)]
        values.sort()
    else:
        max_value = int((interval.length - n*duration)/freq)
        values = [random.randint(0, max_value) for _ in range(n)]
        values.sort()
        values = [value + i*relative_duration for i, value in enumerate(values)]

    left = pd.DatetimeIndex([interval.left + value*freq for value in values])

    return pd.IntervalIndex.from_arrays(
        left=left,
        right=left+duration,
        closed=interval.closed,
        name=name,
    )


# TODO: if an analog tag is not indexed in the interval, calculation values should be NaN
def calculate(intervals: pd.IntervalIndex, tag, operation, name):
    """Perform an aggregation operation on a tag for the dataframe intervals

     Parameters
     ----------
     intervals : pd.IntervalIndex
        The intervals on which to calculate
     tag : Tag
         The tag on which the calculation happens
     operation : str
         mean, min, max, range, start, end, delta, integral, or stdev
     name : str
         Name under which the calculation result needs to be stored in the DataFrame.

     """

    operation = ip.correct_value(operation, CALCULATION_OPTIONS)

    interval_dict = {
        str(i): interval
        for i, interval in enumerate(intervals)
    }

    interval_data = [
        {
            "key": key,  # Assign increasing integer
            "startDate": interval.left.isoformat(timespec="milliseconds"),
            "endDate": interval.right.isoformat(timespec="milliseconds"),
        }
        for key, interval in interval_dict.items()  # Enumerate over the index
    ]

    if interval_data:
        payload = {
            "searchType": operation,
            "tags": [
                {
                    "tagName": tag.name,
                    "timePeriods": interval_data,
                    "shift": int(tag.shift.total_seconds()),
                    "interpolationType": tag._interpolation_payload_str_lower,
                }
            ],
            "filters": [],
        }
        response = tag.client.session.post("/compute/calculate/", json=payload)
        response_data = response.json()
    else:
        response_data = []  # Deal with empty IntervalIndex input

    values = pd.Series(
        name=name,
        data={
            interval_dict[result["key"]]: result.get("value")
            for result in sorted(response_data, key=lambda x: int(x["key"]))  # keep values in same order
        },
    )

    if tag.numeric:
        values = values.astype(float)
    else:
        values = values.map(tag.states, na_action="ignore")
        values = values.astype("string")

    return values
