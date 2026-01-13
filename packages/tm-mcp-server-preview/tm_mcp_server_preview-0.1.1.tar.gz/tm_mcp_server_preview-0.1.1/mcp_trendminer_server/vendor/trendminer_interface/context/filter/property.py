from trendminer_interface.context.filter.base import ContextFilterBase
from trendminer_interface.base import FactoryBase
from trendminer_interface import _input as ip


class PropertyFieldFilter(ContextFilterBase):
    """Filter on 'other property' of context items

    Other properties key-value pairs of the context item `fields` attribute which are not covered by an actual
    `ContextField`.

    Attributes
    ----------
    key : str
        Other property key
    """
    filter_type = "PROPERTY_FIELD_FILTER"

    def __init__(self, client, key, values):
        super().__init__(client=client)
        self.key = key
        self.values = values

    @property
    def values(self):
        """Filter values

        Returns
        -------
        values : list
            List of values on which to filter
        """
        return self._values

    @values.setter
    def values(self, values):
        self._values = ip.any_list(values)

    def _json(self):
        return {
            **super()._json(),
            "key": self.key,
            "values": self.values,
        }


class PropertyFieldFilterFactory(FactoryBase):
    """Factory for creating `other property` context filters"""
    tm_class = PropertyFieldFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        PropertyFieldFilter
        """
        return self.tm_class(client=self.client, key=data["key"], values=data["values"])

    def __call__(self, key, values):
        """Create new 'other property' context filter

        Parameters
        ----------
        key : str
            Other property key
        values : list
            List of values on which to filter
        """
        return self.tm_class(client=self.client, key=key, values=values)

