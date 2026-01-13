from .base import ContextFieldFilterBase

from trendminer_interface.context.field import ContextFieldFactory
from trendminer_interface.base import FactoryBase
from trendminer_interface import _input as ip


class EnumerationFieldFilter(ContextFieldFilterBase):
    """Context filter on enumeration fields"""

    filter_type = "ENUMERATION_FIELD_FILTER"

    def __init__(self, client, field, values, mode):
        super().__init__(client=client, field=field, mode=mode)
        self.values = values

    @property
    def values(self):
        """Filter values

        Returns
        -------
        values : list
            List of values to filter on. Must be values allowed by the field type.
        """

        return self._values

    @values.setter
    def values(self, values):
        self._values = [ip.case_correct(value, value_options=self.field.options) for value in ip.any_list(values)]
        
    def _json(self):
        return {
            **super()._json(),
            "field": self.field.key,
            "fieldIdentifier": self.field.identifier,
            "values": self.values,
        }


class EnumerationFieldFilterFactory(FactoryBase):
    """Factory for creating creation date context filters"""
    tm_class = EnumerationFieldFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        EnumerationFieldFilter
        """
        return self.tm_class(
            client=self.client,
            field=ContextFieldFactory(client=self.client)._from_json(data["customField"]),
            values=data.get("values"),
            mode=data.get("mode")
        )

    def __call__(self, field, values=None, mode=None):
        """Create new enumeration field context filter

        Parameters
        ----------
        field : Any
            A (reference to a) context field
        values : list, optional
            Values to filter on. Must be options of the given enumeration field.
        mode : str, optional
            Search for special conditions, ignoring `values`. "EMPTY" or "NON_EMPTY"

        Returns
        -------
        EnumerationFieldFilter
            Context filter on enumeration field
        """
        return self.tm_class(client=self.client, field=field, values=values, mode=mode)