import pandas as pd
from trendminer_interface.context.filter.base.filter import ContextFilterBase
from trendminer_interface.base import FactoryBase


class IntervalFilter(ContextFilterBase):
    """Filter on context item event or creation time through fixed interval

    Attributes
    ----------
    interval : pandas.Interval
        The time interval on which to filter
    created_date : bool, default False
        Whether we need to filter on creation time rather than event time
    """
    filter_type = 'INTERVAL_FILTER'

    def __init__(self, client, interval, created_date):
        super().__init__(client=client)
        self.interval = interval
        self.created_date = created_date

    def _json(self):
        data = {
            "startDate": self.interval.left.isoformat(timespec="milliseconds"),
            "endDate": self.interval.right.isoformat(timespec="milliseconds"),
            "type": self.filter_type,
        }

        if self.created_date:
            data.update({'intervalType': 'CREATED_DATE'})

        return data


class IntervalFilterFactory(FactoryBase):
    """Factory for creating context interval filter"""
    tm_class = IntervalFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        IntervalFilter
        """
        return self.tm_class(
            client=self.client,
            interval=pd.Interval(
                left=pd.Timestamp(data["startDate"]).tz_convert(self.client.tz),
                right=pd.Timestamp(data["endDate"]).tz_convert(self.client.tz),
                closed="both",
            ),
            created_date=data.get("intervalType") == 'CREATED_DATE'
        )

    def __call__(self, interval, created_date=False):
        """Create new filter on context item interval

        Parameters
        ----------
        interval : pandas.Interval
            Interval on which to filter
        created_date : bool
            Whether we need to filter on creation time rather than event time

        Returns
        -------
        IntervalFilter
            Interval filter on context item event or creation time
        """
        return self.tm_class(client=self.client, interval=interval, created_date=created_date)