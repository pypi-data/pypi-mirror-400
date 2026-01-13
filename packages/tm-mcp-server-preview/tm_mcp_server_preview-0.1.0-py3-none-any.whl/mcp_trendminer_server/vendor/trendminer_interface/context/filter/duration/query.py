import isodate
import pandas as pd

from trendminer_interface.context.filter.base import ContextQueryBase, ContextQueryFactoryBase
from trendminer_interface.base import AsTimedelta


class DurationQuery(ContextQueryBase):
    """Query based on context item duration

    Attributes
    ----------
    value : pandas.Timedelta
        Context item duration criterion
    """
    value = AsTimedelta()

    def __init__(self, client, operator, value):
        super().__init__(client=client, operator=operator, value=value)

    def _json(self):
        return {
            "operator": self.operator_str,
            "value": self.value.isoformat(),
        }


class DurationQueryFactory(ContextQueryFactoryBase):
    """Factory for creating context item duration queries"""
    tm_class = DurationQuery

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        DurationQuery
        """
        # Isodate is required since Timedelta fails on non-fixed length string durations (e.g. Y, M)
        return self.tm_class(
            client=self.client,
            operator=data["operator"],
            value=pd.Timedelta(isodate.parse_duration(data["value"])),
        )
