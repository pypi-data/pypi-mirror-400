from .base import ContextFieldFilterBase
from .query import NumericQueryFactory

from trendminer_interface.context.field import ContextFieldFactory
from trendminer_interface.base import ByFactory, FactoryBase


class NumericFieldFilter(ContextFieldFilterBase):
    """Context filter on numeric fields

    Attributes
    ----------
    values : list
        List of (entries convertible to) NumericQuery
    """
    filter_type = "NUMERIC_FIELD_FILTER"
    values = ByFactory(NumericQueryFactory, "_list")

    def __init__(self, client, field, values, mode):
        super().__init__(client=client, field=field, mode=mode)
        self.values = values
        
    def _json(self):
        return {
            **super()._json(),
            "field": self.field.key,
            "fieldIdentifier": self.field.identifier,
            "conditions": [value._json() for value in self.values] if self.values else None,  # empty list gives error
        }


class NumericFieldFilterFactory(FactoryBase):
    """Factory for creating and retrieving Numeric field context filters"""
    tm_class = NumericFieldFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        NumericFieldFilter
        """
        return self.tm_class(
            client=self.client,
            field=ContextFieldFactory(client=self.client)._from_json(data["customField"]),
            values=data.get("conditions"),
            mode=data.get("mode")
        )

    def __call__(self, field, values=None, mode=None):
        """Create new numeric field context filter

        Parameters
        ----------
        field : Any
            A (reference to a) context field
        values : list, optional
            List of (entries convertible to) NumericQuery to filter on.
        mode : str, optional
            Search for special conditions, ignoring `values`. "EMPTY" or "NON_EMPTY"

        Returns
        -------
        NumericFieldFilter
            Context filter on numeric field
        """
        return self.tm_class(client=self.client, field=field, values=values, mode=mode)
