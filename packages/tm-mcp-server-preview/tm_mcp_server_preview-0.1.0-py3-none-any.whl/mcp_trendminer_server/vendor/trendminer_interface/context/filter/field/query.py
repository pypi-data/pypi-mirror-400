from trendminer_interface.context.filter.base import ContextQueryBase, ContextQueryFactoryBase


class NumericQuery(ContextQueryBase):
    """Filter on context field (in)equality to give value"""
    def __init__(self, client, operator, value):
        super().__init__(client=client, operator=operator, value=value)

    @property
    def value(self):
        """Filter value

        Returns
        -------
        value : float
            Numeric value to filter on
        """
        return self._value

    @value.setter
    def value(self, value):
        self._value = float(value)

    def _json(self):
        return {
            "operator": self.operator_str,
            "value": self.value,
        }


class NumericQueryFactory(ContextQueryFactoryBase):
    """Factory for creating NumericQuery"""
    tm_class = NumericQuery

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        return self.tm_class(client=self.client, operator=data["operator"], value=data["value"])
