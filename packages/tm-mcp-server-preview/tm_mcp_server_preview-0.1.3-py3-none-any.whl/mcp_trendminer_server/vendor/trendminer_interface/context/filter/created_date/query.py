from trendminer_interface.context.filter.base import ContextQueryBase, ContextQueryFactoryBase
from trendminer_interface.base import AsTimestamp


class CreatedDateQuery(ContextQueryBase):
    """Creation date query for creation date context filters

    Attributes
    ----------
    value : pandas.Timestamp
        Creation timestamp criterion
    """
    value = AsTimestamp()

    def __init__(self, client, operator, value):
        super().__init__(client=client, operator=operator, value=value)

    def _json(self):
        return {
            "operator": self.operator_str,
            "createdDate": self.value.isoformat(timespec="milliseconds"),
        }


class DateQueryFactory(ContextQueryFactoryBase):
    """Factory for making creation date queries"""
    tm_class = CreatedDateQuery

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        CreatedDateQuery
        """
        return self.tm_class(client=self.client, operator=data["operator"], value=data["createdDate"])
