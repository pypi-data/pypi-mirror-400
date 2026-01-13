import pandas as pd
import numpy as np
import random
import trendminer_interface._input as ip

from .functions import sample, calculate


@pd.api.extensions.register_dataframe_accessor("interval")
class IntervalDataFrameAccessor:
    """Custom accessor for interval-based calculations and utilities

    This accessor is applicable to any DataFrame which has an IntervalIndex based on timezone-aware timestamps. It
    contains a method for performing TrendMiner-based calculations on the intervals represented by the IntervalIndex, as
    well as some more generic utility methods for manipulating the IntervalIndex itself.

    Methods always return a modified DataFrame, they do not edit in place.

    The idea of this accessor is to provide users with an interface to chain multiple calculations and interval
    operations to gather the data needed for their analysis, directly in the format (a pandas DataFrame) in which their
    custom analysis will likely take place.
    """

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if not isinstance(obj.index.dtype, pd.IntervalDtype):
            raise AttributeError("Methods can only be applied on DataFrame with IntervalIndex index")

    def set_closed(self, closed):
        """Set the closed attribute of the DataFrame index

        Parameters
        ----------
        closed : str
            left, right, both or neither

        Returns
        -------
        df : pandas.DataFrame
            DataFrame of intervals with altered DataFrame.index.closed
        """
        return self._obj.set_index(
            self._obj.index.set_closed(closed)
        )

    def _set_interval(self, left, right, name, drop):
        new_index = pd.IntervalIndex.from_arrays(
            left=left if left is not None else self._obj.index.left,
            right=right if right is not None else self._obj.index.right,
            closed=self._obj.index.closed,
            name=name,
            dtype=self._obj.index.dtype,
        )

        return (
            self._obj
            .reset_index(drop=drop)
            .set_index(new_index, drop=drop)
        )

    def _move_interval(self, left, right, name, drop):
        if left is not None:
            left = self._obj.index.left + pd.Timedelta(left)
        if right is not None:
            right = self._obj.index.right + pd.Timedelta(right)
        return self._set_interval(left=left, right=right, name=name, drop=drop)

    def shift(self, by, name=None, drop=True):
        """Shift intervals by a given timedelta

        Parameters
        ----------
        by : pandas.Timedelta
            How much to shift the IntervalIndex. Positive values shift the intervals forward to a later time, while
            negative values shift backwards to an earlier time
        name : str, optional
            Name of the new IntervalIndex
        drop : bool, default True
            Whether to drop the original IntervalIndex, or keep it as a column in the DataFrame (under its original name)

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with shifted IntervalIndex
        """
        by = pd.Timedelta(by)
        return self._move_interval(left=by, right=by, name=name, drop=drop)

    def grow(self, left=None, right=None, name=None, drop=True):
        """Extend the intervals in the index outwards, setting a new IntervalIndex

        Parameters
        ----------
        left : pandas.Timedelta, optional
            How much to extend the interval left (start) point
        right : pandas.Timedelta, optional
            How much to extend the interval right (end) point
        name : str, optional
            Name of the new IntervalIndex
        drop : bool, default True
            Whether to drop the original IntervalIndex, or keep it as a column in the DataFrame (under its original name)

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with extended IntervalIndex
        """
        if left is not None:
            left = -pd.Timedelta(left)
        return self._move_interval(left=left, right=right, name=name, drop=drop)

    def shrink(self, left=None, right=None, name=None, drop=True):
        """Shrink the intervals in the index inwards, setting a new IntervalIndex

        Parameters
        ----------
        left : pandas.Timedelta, optional
            How much to shrink the interval left (start) point
        right : pandas.Timedelta, optional
            How much to shrink the interval right (end) point
        name : str, optional
            Name of the new IntervalIndex
        drop : bool, default True
            Whether to drop the original IntervalIndex, or keep it as a column in the DataFrame (under its original name)

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with shrunken IntervalIndex
        """
        if right is not None:
            right = -pd.Timedelta(right)
        return self._move_interval(left=left, right=right, name=name, drop=drop)

    def after_start(self, length, name=None, drop=True):
        """Set an IntervalIndex of given length with the same starts as the current IntervalIndex

        Parameters
        ----------
        length : pandas.Timedelta
            The length of the intervals in the new IntervalIndex
        name : str, optional
            Name of the new IntervalIndex
        drop : bool, default True
            Whether to drop the original IntervalIndex, or keep it as a column in the DataFrame (under its original name)

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with new IntervalIndex
        """
        return self._set_interval(
            right=self._obj.index.left + pd.Timedelta(length),
            left=None, name=name, drop=drop,
        )

    def after_end(self, length, name=None, drop=True):
        """Set an IntervalIndex with intervals of given length that follows right after the current IntervalIndex

        Parameters
        ----------
        length : pandas.Timedelta
            The length of the intervals in the new IntervalIndex
        name : str, optional
            Name of the new IntervalIndex
        drop : bool, default True
            Whether to drop the original IntervalIndex, or keep it as a column in the DataFrame (under its original name)

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with new IntervalIndex
        """
        return self._set_interval(
            left=self._obj.index.right,
            right=self._obj.index.right + pd.Timedelta(length),
            name=name, drop=drop,
        )

    def before_start(self, length, name=None, drop=True):
        """Set an IntervalIndex with intervals of given length that falls right before the current IntervalIndex

        Parameters
        ----------
        length : pandas.Timedelta
            The length of the intervals in the new IntervalIndex
        name : str, optional
            Name of the new IntervalIndex
        drop : bool, default True
            Whether to drop the original IntervalIndex, or keep it as a column in the DataFrame (under its original name)

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with new IntervalIndex
        """
        return self._set_interval(
            left=self._obj.index.left - pd.Timedelta(length),
            right=self._obj.index.left,
            name=name, drop=drop,
        )

    def before_end(self, length, name=None, drop=True):
        """Set an IntervalIndex with intervals of given length with the same ends as the current IntervalIndex

        Parameters
        ----------
        length : pandas.Timedelta
            The length of the intervals in the new IntervalIndex
        name : str, optional
            Name of the new IntervalIndex
        drop : bool, default True
            Whether to drop the original IntervalIndex, or keep it as a column in the DataFrame (under its original name)

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with new IntervalIndex
        """
        return self._set_interval(
            left=self._obj.index.right - pd.Timedelta(length),
            right=None, name=name, drop=drop,
        )

    def round(self, freq, left="shrink", right="shrink"):
        """Round the intervals to a given frequency

        Parameters
        ----------
        freq : pd.Timedelta
            Rounding frequency
        left : str, default 'shrink'
            - 'shrink' round interval start timestamp inwards, shrinking the interval
            - 'grow' round interval start timestamp outwards, growing the interval
            - 'nearest' round interval start timestamp to the nearest rounded timestamp
        right : str, default 'shrink'
            - 'shrink' round interval end timestamp inwards, shrinking the interval
            - 'grow' round interval end timestamp outwards, growing the interval
            - 'nearest' round interval end timestamp to the nearest rounded timestamp

        Returns
        -----
        df : pandas.DataFrame
            DataFrame with rounded IntervalIndex
        """

        freq = pd.Timedelta(freq)

        value_options = ["shrink", "grow", "nearest"]
        left = ip.case_correct(left, value_options)
        right = ip.case_correct(right, value_options)

        if left == "shrink":
            new_left = self._obj.index.left.ceil(freq)
        elif left == "grow":
            new_left = self._obj.index.left.floor(freq)
        elif left == "nearest":
            new_left = self._obj.index.left.round(freq)
        else:
            raise ValueError(left)

        if right == "shrink":
            new_right = self._obj.index.right.floor(freq)
        elif right == "grow":
            new_right = self._obj.index.right.ceil(freq)
        elif right == "nearest":
            new_right = self._obj.index.right.round(freq)
        else:
            raise ValueError(right)

        return self._set_interval(left=new_left, right=new_right, name=self._obj.index.name, drop=True)

    def group_overlapping(self):
        """Group overlapping intervals

        Returns
        -------
        pandas.DataFrameGroupBy

        Notes
        -----
        This method will not group intervals that simply touch (i.e. when one interval's `left` is the other interval's
        `right`, but the `IntervalIndex.closed` is `left`, `right` or `neither`).
        """

        # List of intervals. Longer intervals first for speed.
        intervals = sorted(self._obj.index, key=lambda x: x.length, reverse=True)

        new_intervals = []
        while len(intervals) > 0:
            current_interval = intervals[0]
            overlapping = [current_interval]
            non_overlapping = []
            for interval in intervals[1:]:
                if current_interval.overlaps(interval):
                    overlapping.append(interval)
                else:
                    non_overlapping.append(interval)

            if len(overlapping) == 1:
                new_intervals.append(current_interval)
                intervals = non_overlapping
            else:
                new_start = min([interval.left for interval in overlapping])
                new_end = max([interval.right for interval in overlapping])
                current_interval = pd.Interval(left=new_start, right=new_end, closed=current_interval.closed)
                intervals = [current_interval] + non_overlapping

        new_index = pd.IntervalIndex(
            new_intervals,
            name=self._obj.index.name,
            closed=self._obj.index.closed,
        )

        return self._obj.groupby(
            lambda interval: new_index[new_index.overlaps(interval)].item(),
            sort=True,
        )

    def calculate(self, tag, operation, name):
        """Perform an aggregation operation on a tag for the `DataFrame.IntervalIndex` intervals

        Parameters
        ----------
        tag : Tag
            The tag on which the operation happens
        operation : str
            mean, min, max, range, start, end, delta, integral, or stdev
        name : str
            Name under which the calculation result needs to be stored in the DataFrame.

        Returns
        -------
        pandas.DataFrame
            DataFrame with additional or updated column with the aggregated tag values for the intervals
        """
        values = calculate(intervals=self._obj.index, tag=tag, operation=operation, name=name)

        df = self._obj.copy()
        df[name] = values
        return df

    def invert(self, name, span=None):
        """Get the intervals inbetween the current intervals

        The output will be sorted from oldest to newest intervals.

        Parameters
        ----------
        name : str
            Name of the new, inverted IntervalIndex
        span : pandas.Interval, optional
            Range over which the intervals need to be inverted. When given, the time from the start of the span to the
            start of the first input interval, and the time from the last input interval to the end of the range are
            also returned as part of the inverted intervals, as long as they are not shorter than the index resolution
            (to avoid small intervals at the edges as a result of rounding). The span needs to encompass all input
            intervals. When no span is given, only the intervals inbetween the input intervals are returned as inverted
            intervals.

        Returns
        -------
        pandas.DataFrame
            Empty DataFrame with inverted IntervalIndex

        Notes
        -----
        The `closed` attribute of the IntervalIndex will invert 'neither' <-> 'both', while 'left' and 'right' will stay
        unchanged.

        """

        empty_df = pd.DataFrame(index=self._obj.index)

        # Handle span
        if span is not None:

            # Keep only original intervals that overlap with the span
            empty_df = empty_df[empty_df.index.overlaps(span)]

            # Add zero length intervals at the edges of the span
            dummy_intervals = pd.DataFrame(
                index=pd.IntervalIndex.from_arrays(
                    left=[span.left, span.right],
                    right=[span.left, span.right],
                    closed=empty_df.index.closed,
                    name=empty_df.index.name,
                )
            )
            empty_df = pd.concat([empty_df, dummy_intervals])

        # Get non-overlapping initial index
        merged_index = empty_df.interval.group_overlapping().first().index

        inverted_closed = {
            "left": "left",
            "right": "right",
            "both": "neither",
            "neither": "both",
        }[merged_index.closed]

        inverted_index = pd.IntervalIndex.from_arrays(
            left=merged_index.right[:-1],
            right=merged_index.left[1:],
            closed=inverted_closed,
            name=name,
        )

        return pd.DataFrame(index=inverted_index)

    def has_overlaps(self):
        """Check if the intervals contain overlaps

        Returns
        -------
        has_overlaps : bool
            Whether the DataFrame IntervalIndex has overlaps
        """
        sorted_index = self._obj.index.sort_values()
        for i1, i2 in zip(sorted_index[:-1], sorted_index[1:]):
            if i1.overlaps(i2):
                return True
        return False

    def get_span(self) -> pd.Interval:
        """Get the interval encompassing all intervals in the index

        Returns
        -------
        span : pandas.Interval
            The interval spanning the full IntervalIndex
        """
        return pd.Interval(
            left=min([i.left for i in self._obj.index]),
            right=max([i.right for i in self._obj.index]),
            closed=self._obj.index.closed,
        )

    def sample(self, duration, n=1, overlap=False, freq=pd.Timedelta(minutes=1), drop=True, name="samples"):
        """Sample random sub-intervals from a given list of intervals

        Parameters
        ----------
        duration : pandas.Timedelta
            Duration of the sample intervals
        n : int, default 1
            Number of intervals to return
        overlap : bool, default False
            Whether the returned sample intervals can overlap
        freq : pandas.Timedelta, default 1m
            The resolution to which all inputs and outputs will be rounded. Defaults to client index resolution.
        drop : bool, default True
            Whether to drop the original IntervalIndex in the returned DataFrame
        name : str, default 'samples'
            Name of the new IntervalIndex column of samples

        Returns
        -------
        samples : pandas.DataFrame
            DataFrame with sampled intervals as index

        Notes
        -----
        Intervals will be rounded down to the given freq before sampling.

        The sampling method first determines how many sample should be taken per interval, and then iteratively
        samples that number of sub-intervals from each interval. The number of samples per interval are distributed
        randomly proportional to the number of possible sample positions within an interval. An interval can be sampled
        in `(interval length - duration)/freq + 1` possible ways. For example, there is only 1 way to take a 1h sample
        out of a 1h interval, while for a freq of 1m there are 60 ways of taking a 1h sample out of a 2h interval.

        When the `IntervalIndex.closed` property is `both` it is possible that two samples theoretically overlap at
        their endpoints even when `overlap=False`.
        """

        freq = pd.Timedelta(freq)
        duration = pd.Timedelta(duration)

        df = self.round(freq=freq, left="shrink", right="shrink")

        # Determine how many samples to draw from each interval
        if overlap:
            weights = np.clip(
                (df.index.length - duration) / freq + 1,
                a_min=0, a_max=None,
            )

            sample_count = (
                pd.Series(
                    data=1,
                    index=pd.IntervalIndex(random.choices(df.index, weights=weights, k=n))
                )
                .groupby(level=0).sum()
                .reindex(df.index, fill_value=0)
            )

        else:
            # Initialize sample count dataframe
            sample_count = pd.Series(
                index=df.index,
                data=0,
            )

            # Iteratively distribute n samples across intervals
            for i in range(0, n):

                # The weight for being sampled is proportional to the duration that would be left to take a sample
                weights = np.clip(
                    (df.index.length - (1 + sample_count) * duration) / freq + 1,
                    a_min=0, a_max=None,
                )
                if weights.sum() == 0:
                    raise ValueError(f"Cannot generate {n} non-overlapping '{duration}' samples from given intervals")
                choice = random.choices(sample_count.index, weights=weights, k=1)[0]
                sample_count[choice] += 1

        # required step to keep original (rather than rounded) index when drop=False
        # df has the rounded IntervalIndex, while self._obj has the original
        if drop:
            df_iter = df
        else:
            df_iter = self._obj.reset_index(drop=False)

        k = 0
        samples_list = []
        for i, row in df_iter.iterrows():
            interval = i if drop else df.index[i]  # always take rounded interval here
            samples = pd.DataFrame(
                index=sample(
                    interval=interval,
                    duration=duration,
                    n=sample_count.iloc[k],
                    overlap=overlap,
                    freq=freq,
                    name=name,
                ),
                columns=row.index,
            )
            samples[:] = row.values
            if not len(samples) == 0:
                samples_list.append(samples)
            k += 1

        return pd.concat(samples_list)
