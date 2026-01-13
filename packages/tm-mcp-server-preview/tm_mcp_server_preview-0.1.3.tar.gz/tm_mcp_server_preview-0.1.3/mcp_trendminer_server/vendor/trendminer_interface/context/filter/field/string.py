from .base import ContextFieldFilterBase

from trendminer_interface.context.field import ContextFieldFactory
from trendminer_interface.base import FactoryBase
from trendminer_interface import _input as ip


class StringFieldFilter(ContextFieldFilterBase):
    """Context filter on string fields"""
    filter_type = "STRING_FIELD_FILTER"

    def __init__(self, client, field, values, mode):
        super().__init__(client=client, field=field, mode=mode)
        self.values = values

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = ip.any_list(values)
        
    def _json(self):
        return {
            **super()._json(),
            "field": self.field.key,
            "fieldIdentifier": self.field.identifier,
            "values": self.values if self.values else None,  # empty list gives error
        }


class StringFieldFilterFactory(FactoryBase):
    """Factory for creating string field context filters"""
    tm_class = StringFieldFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        StringFieldFilter
        """
        return self.tm_class(
            client=self.client,
            field=ContextFieldFactory(client=self.client)._from_json(data["customField"]),
            values=data.get("values"),
            mode=data.get("mode")
        )

    def __call__(self, field, values=None, mode=None):
        """Create new string field context filter

        Parameters
        ----------
        field : Any
            A (reference to a) context field
        values : list, optional
            Values to filter on
        mode : str, optional
            Search for special conditions, ignoring `values`. "EMPTY" or "NON_EMPTY"

        Returns
        -------
        StringFieldFilter
            Context filter on string field
        """
        return self.tm_class(client=self.client, field=field, values=values, mode=mode)
