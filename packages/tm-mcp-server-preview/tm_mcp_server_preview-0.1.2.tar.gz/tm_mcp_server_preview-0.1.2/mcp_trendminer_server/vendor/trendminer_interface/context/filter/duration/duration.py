from .query import DurationQueryFactory
from trendminer_interface.context.filter.base import ContextFilterBase
from trendminer_interface.base import ByFactory, FactoryBase


class DurationFilter(ContextFilterBase):
    """Filter on context item duration

    Attributes
    ----------
    conditions : list of DurationQuery
        Duration-based queries on which to filter
    """
    filter_type = "DURATION_FILTER"
    conditions = ByFactory(DurationQueryFactory, "_list")

    def __init__(self, client, conditions):
        super().__init__(client=client)
        self.conditions = conditions

    def _json(self):
        return {
            **super()._json(),
            "conditions": [condition._json() for condition in self.conditions],
        }


class DurationFilterFactory(FactoryBase):
    """Factory for creating context item duration filters"""
    tm_class = DurationFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        DurationFilter
        """
        return self.tm_class(client=self.client, conditions=data["conditions"])

    def __call__(self, conditions):
        """Create new context item duration filter

        Parameters
        ----------
        conditions : list
            List of entries convertible to DurationQuery

        Returns
        -------
        DurationFilter
            Filter on context item duration
        """
        return self.tm_class(client=self.client, conditions=conditions)
