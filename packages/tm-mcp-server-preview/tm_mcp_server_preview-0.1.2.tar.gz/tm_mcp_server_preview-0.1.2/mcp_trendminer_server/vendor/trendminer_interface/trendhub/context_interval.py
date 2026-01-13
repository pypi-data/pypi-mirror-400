import pandas as pd
from trendminer_interface.base import SerializableBase, FactoryBase, HasOptions
from trendminer_interface.constants import CONTEXT_INTERVAL_OPTIONS


class ContextChartInterval(SerializableBase):
    """TrendHub view context chart interval

    The context chart interval of a TrendHub view sets the interval of the secondary time-series graph (the context
    chart). This interval determines the time-series data to be included in analytics performed while the TrendHub view
    is open (e.g., searches will only retrieve results from the context chart interval).

    The somewhat confusingly named context chart interval is thus in no way linked to ContextHub or context items.

    Attributes
    ----------
    interval : pandas.Interval
        The time interval contained by the context interval
    interval_type : str
        CUSTOM_CONTEXT_TIMESPAN or PREDEFINED_CONTEXT_TIMESPAN_RANGE. Does not seem to have an affect, but view will
        show unsaved changes if it changes.
    interval_range : dict
        Info that is sometimes present on a saved TrendHub view. Does not seem to have an affect, but view will show
        unsaved changes if it changes.
    """
    interval_type = HasOptions(CONTEXT_INTERVAL_OPTIONS)

    def __init__(self, client, interval, interval_type, interval_range):
        super().__init__(client=client)
        self.interval = interval
        self.interval_type = interval_type
        self.interval_range = interval_range

    def _json(self):
        payload= {
            "startDate": self.interval.left.isoformat(timespec="milliseconds"),
            "endDate": self.interval.right.isoformat(timespec="milliseconds"),
            "type": self.interval_type,
        }

        if self.interval_range is not None:
            payload.update({"contextTimeSpanRange": self.interval_range})

        return payload


class ContextChartIntervalFactory(FactoryBase):
    """Factory for TrendHub context intervals"""
    tm_class = ContextChartInterval

    def __init__(self, client):
        super().__init__(client=client)

    def from_interval(self, interval):
        """Create a context interval from a regular interval

        Attributes
        ----------
        interval : pandas.Interval
            Input interval

        Returns
        -------
        ContextChartInterval
        """
        # only allowing creation of custom timespans is sufficient
        if not isinstance(interval, pd.Interval):
            raise TypeError("Expected pandas.Interval type")

        return self.tm_class(
            client=self.client,
            interval=interval,
            interval_type="CUSTOM_CONTEXT_TIMESPAN",
            interval_range=None,
        )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        ContextChartInterval
        """
        return self.tm_class(
            client=self.client,
            interval=pd.Interval(
                left=pd.Timestamp(data["startDate"]).tz_convert(self.client.tz),
                right=pd.Timestamp(data["endDate"]).tz_convert(self.client.tz),
                closed="both",
            ),
            interval_type=data["type"],
            interval_range=data.get("contextTimeSpanRange"),
        )

    @property
    def _get_methods(self):
        return self.from_interval,