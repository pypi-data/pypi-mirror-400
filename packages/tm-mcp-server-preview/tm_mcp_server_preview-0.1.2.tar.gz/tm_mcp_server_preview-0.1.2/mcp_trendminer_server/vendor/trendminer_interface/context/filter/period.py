import isodate
import pandas as pd

from trendminer_interface.context.filter.base.filter import ContextFilterBase
from trendminer_interface.base import AsTimedelta, FactoryBase


class PeriodFilter(ContextFilterBase):
    """Filter on context item event time with dynamic period

    Attributes
    ----------
    period : pandas.Timedelta
        Duration marking a time interval running up to the current time, on which to filter the context items
    live : bool
        Whether the ContexHubView having this filter needs to update live
    """
    filter_type = 'PERIOD_FILTER'
    period = AsTimedelta()

    def __init__(self, client, period, live):
        super().__init__(client=client)
        self.period = period
        self.live = live

    def _json(self):
        return {
            "live": self.live,
            "type": self.filter_type,
            "period": self.period.isoformat(),
        }


class PeriodFilterFactory(FactoryBase):
    """Factory for creating period filter on context item event time"""
    tm_class = PeriodFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        PeriodFilter
        """
        # Isodate is required since Timedelta fails on non-fixed length string durations (e.g. Y, M)
        return self.tm_class(
            client=self.client,
            period=pd.Timedelta(isodate.parse_duration(data["period"])),
            live=data["live"]
        )

    def __call__(self, period='8h', live=False):
        """Create new period filter for context item event time

        Attributes
        ----------
        period : Period or str
            Period on which to filter
        live : bool
            Whether the ContexHubView having this filter needs to update live
        """
        return self.tm_class(client=self.client, period=period, live=live)
