import pandas as pd
import trendminer_interface._input as ip

from .functions import sample, calculate


@pd.api.extensions.register_series_accessor("interval")
class IntervalSeriesAccessor:
    """Custom accessor for interval-based calculations and utilities

    This accessor is applicable to any Series of which `name` is an object of the `pandas.Interval` based on
    timezone-aware timestamps. It contains a method for performing TrendMiner-based calculations on the intervals
    represented by the `Series.name` interval, as more generic utility methods for manipulating the interval itself.

    The convention that the `Series.name` is of the `pandas.Interval` type, follows from the representation of a group
    of interval-based items (e.g. search results or context items) as a DataFrame with IntervalIndex. It is assumed that
    users want to do manipulations and calculations on those items in parallel, for which the DataFrame is a great
    format. This accessor for calculations/manipulations on a single interval has identical or similar methods as the
    `DataFrame.interval` custom accessor.

    Methods always return a modified Series, they do not edit in place.
    """

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if not isinstance(obj.name, pd.Interval):
            raise AttributeError("Methods can only be applied on DataFrame with IntervalIndex index")

    def set_closed(self, closed):
        """Set the closed attribute of the Series name

        Parameters
        ----------
        closed : str
            left, right, both or neither

        Returns
        -------
        ser : pandas.Series
            Series with altered Series.name Interval
        """
        return self._set_interval(
            left=self._obj.name.left,
            right=self._obj.name.right,
            closed=closed,
            keep_as=None,
        )

    def _set_interval(self, left, right, closed, keep_as):
        ser = self._obj.copy()
        ser.name = pd.Interval(
            left=left if left is not None else self._obj.name.left,
            right=right if right is not None else self._obj.name.right,
            closed=closed,
        )

        if keep_as is not None:
            ser[keep_as] = self._obj.name

        return ser

    def _move_interval(self, left, right, keep_as):
        if left is not None:
            left = self._obj.name.left + pd.Timedelta(left)
        if right is not None:
            right = self._obj.name.right + pd.Timedelta(right)
        return self._set_interval(left=left, right=right, closed=self._obj.name.closed, keep_as=keep_as)

    def shift(self, by, keep_as=None):
        """Shift the interval by a given timedelta

        Parameters
        ----------
        by : pandas.Timedelta
            How much to shift the IntervalIndex. Positive values shift the intervals forward to a later time, while
            negative values shift backwards to an earlier time
        keep_as : str, optional
            Whether to keep the current interval in the Series while `Series.name` is set to a new value, and if so,
            under what index

        Returns
        -------
        ser : pandas.Series
            Series with shifted `Series.name`
        """
        return self._move_interval(left=by, right=by, keep_as=keep_as)

    def grow(self, left=None, right=None, keep_as=None):
        """Extend the interval outwards, setting a new Series.name

        Parameters
        ----------
        left : pandas.Timedelta, optional
            How much to extend the interval left (start) point
        right : pandas.Timedelta, optional
            How much to extend the interval right (end) point
        keep_as : str, optional
            Whether to keep the current interval in the Series while `Series.name` is set to a new value, and if so,
            under what index
        Returns
        -------
        ser : pandas.Series
            Series with extended `Series.name`
        """
        if left is not None:
            left = -pd.Timedelta(left)
        return self._move_interval(left=left, right=right, keep_as=keep_as)

    def shrink(self, left=None, right=None, keep_as=None):
        """Shrink the interval inwards, setting a new Series.name

        Parameters
        ----------
        left : pandas.Timedelta, optional
            How much to shrink the interval left (start) point
        right : pandas.Timedelta, optional
            How much to shrink the interval right (end) point
        keep_as : str, optional
            Whether to keep the current interval in the Series while `Series.name` is set to a new value, and if so,
            under what index
        Returns
        -------
        ser : pandas.Series
            Series with extended `Series.name` interval
        """
        if right is not None:
            right = -pd.Timedelta(right)
        return self._move_interval(left=left, right=right, keep_as=keep_as)

    def after_start(self, length, keep_as=None):
        """Set interval of given length with the same start as the current `Series.name`

        Parameters
        ----------
        length : pandas.Timedelta
            The length of the intervals in the new IntervalIndex
        keep_as : str, optional
            Whether to keep the current interval in the Series while `Series.name` is set to a new value, and if so,
            under what index

        Returns
        -------
        ser : pandas.Series
            Series with new `Series.name` interval
        """
        return self._set_interval(
            right=self._obj.name.left + pd.Timedelta(length),
            left=None,
            closed=self._obj.name.closed,
            keep_as=keep_as,
        )

    def after_end(self, length, keep_as=None):
        """Set interval of given length that follows right after the current `Series.name`

        Parameters
        ----------
        length : pandas.Timedelta
            The length of the intervals in the new IntervalIndex
        keep_as : str, optional
            Whether to keep the current interval in the Series while `Series.name` is set to a new value, and if so,
            under what index

        Returns
        -------
        ser : pandas.Series
            Series with new `Series.name` interval
        """
        return self._set_interval(
            left=self._obj.name.right,
            right=self._obj.name.right + pd.Timedelta(length),
            closed=self._obj.name.closed,
            keep_as=keep_as,
        )

    def before_start(self, length, keep_as=None):
        """Set interval of given length that falls right before the current `Series.name`

        Parameters
        ----------
        length : pandas.Timedelta
            The length of the intervals in the new IntervalIndex
        keep_as : str, optional
            Whether to keep the current interval in the Series while `Series.name` is set to a new value, and if so,
            under what index

        Returns
        -------
        ser : pandas.Series
            Series with new `Series.name` interval
        """
        return self._set_interval(
            left=self._obj.name.left - pd.Timedelta(length),
            right=self._obj.name.left,
            closed=self._obj.name.closed,
            keep_as=keep_as,
        )

    def before_end(self, length, keep_as=None):
        """Set interval of given length with the same end as the current `Series.name`

        Parameters
        ----------
        length : pandas.Timedelta
            The length of the intervals in the new IntervalIndex
        keep_as : str, optional
            Whether to keep the current interval in the Series while `Series.name` is set to a new value, and if so,
            under what index

        Returns
        -------
        ser : pandas.Series
            Series with new `Series.name` interval
        """
        return self._set_interval(
            left=self._obj.name.right - pd.Timedelta(length),
            right=None,
            closed=self._obj.name.closed,
            keep_as=keep_as,
        )

    def round(self, freq, left="shrink", right="shrink"):
        """Round the interval to a given frequency

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
        -------
        ser : pandas.Series
            Series with rounded `Series.name` interval
        """

        freq = pd.Timedelta(freq)

        value_options = ["shrink", "grow", "nearest"]
        left = ip.case_correct(left, value_options)
        right = ip.case_correct(right, value_options)

        if left == "shrink":
            new_left = self._obj.name.left.ceil(freq)
        elif left == "grow":
            new_left = self._obj.name.left.floor(freq)
        elif left == "nearest":
            new_left = self._obj.name.left.round(freq)
        else:
            raise ValueError(left)

        if right == "shrink":
            new_right = self._obj.name.right.floor(freq)
        elif right == "grow":
            new_right = self._obj.name.right.ceil(freq)
        elif right == "nearest":
            new_right = self._obj.name.right.round(freq)
        else:
            raise ValueError(right)

        return self._set_interval(left=new_left, right=new_right, closed=self._obj.name.closed, keep_as=None)

    def calculate(self, tag, operation, name):
        """Perform an aggregation operation on a tag for the dataframe intervals

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
        pandas.Series
            Series with additional or updated value, resulting from the tag aggregation
        """
        intervals = pd.IntervalIndex([self._obj.name])
        values = calculate(intervals=intervals, tag=tag, operation=operation, name=name)

        ser = self._obj.copy()
        ser[name] = values.iloc[0]
        return ser

    def sample(self, duration, n=1, overlap=False, freq=pd.Timedelta(minutes=1), name="samples", keep_as=None):
        """Sample random sub-intervals from the current interval

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
        name : str, default 'samples'
            Name of the new IntervalIndex column of samples
        keep_as : str, optional
            Keeps the current interval (`Series.name`) as a column with this name in the samples DataFrame

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
        in (interval length - duration)/freq + 1 possible ways. For example, there is only 1 way to take a 1h sample out
        of a 1h interval, while for a freq of 1m there are 60 ways of taking a 1h sample out of a 2h interval.
        """

        freq = pd.Timedelta(freq)
        duration = pd.Timedelta(duration)

        interval = self.round(freq=freq, left="shrink", right="shrink").name

        samples = pd.DataFrame(
            index=sample(
                interval=interval,
                duration=duration,
                n=n,
                overlap=overlap,
                freq=freq,
                name=name,
            ),
            data=self._obj.to_dict(),
        )

        if keep_as:
            samples.insert(0, column=keep_as, value=self._obj.name)

        return samples
