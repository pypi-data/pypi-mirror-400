from trendminer_interface.context.filter.base.filter import ContextFilterBase
from trendminer_interface.base import FactoryBase, ByFactory
from trendminer_interface.user import UserFactory


class CreatedByFilter(ContextFilterBase):
    """Filter on context item creator

    Attributes
    ----------
    users : list of User or ClientUser
        Users on which to filter
    """
    filter_type = "CREATED_BY_FILTER"
    users = ByFactory(UserFactory, "_list")

    def __init__(self, client, users):
        super().__init__(client=client)
        self.users = users

    def _json(self):
        return {
            **super()._json(),
            "users": [user._json() for user in self.users],
        }


class CreatedByFilterFactory(FactoryBase):
    """Factory for created-by context filter creation"""
    tm_class = CreatedByFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        CreatedByFilter
        """
        return self.tm_class(
            client=self.client,
            users=[
                UserFactory(client=self.client)._from_json_work(user)
                for user in data["userDetails"]
            ]
        )

    def __call__(self, users):
        """Create new CreatedByFilter

        Parameters
        ----------
        users : list
            List of (reference to) User or ClientUser


        Returns
        -------
        CreatedByFilter
            Filter on context item creator
        """
        return self.tm_class(client=self.client, users=users)
