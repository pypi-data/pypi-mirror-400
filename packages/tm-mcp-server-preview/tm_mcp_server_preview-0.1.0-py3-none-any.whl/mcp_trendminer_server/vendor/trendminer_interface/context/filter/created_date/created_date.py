from .query import DateQueryFactory
from trendminer_interface.context.filter.base import ContextFilterBase
from trendminer_interface.base import FactoryBase, ByFactory


class CreatedDateFilter(ContextFilterBase):
    """Context item creation date filter

    condition : DateQuery
        Query based on the context item creation date
    """
    filter_type = "CREATED_DATE_FILTER"
    condition = ByFactory(DateQueryFactory)

    def __init__(self, client, condition):
        super().__init__(client=client)
        self.condition = condition

    def _json(self):
        return {
            **super()._json(),
            **self.condition._json(),
        }


class CreatedDateFilterFactory(FactoryBase):
    """Factory for creating creation date context filters"""
    tm_class = CreatedDateFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        CreatedDateFilter
        """
        return self.tm_class(
            client=self.client,
            condition=DateQueryFactory(client=self.client)._from_json(data)
        )

    def __call__(self, condition):
        """Create new creation date context filter

        Parameters
        ----------
        condition : Any
            Input convertible to DateQuery

        Returns
        -------
        CreatedDateFilter
            Filter on context item creation date
        """
        return self.tm_class(client=self.client, condition=condition)
