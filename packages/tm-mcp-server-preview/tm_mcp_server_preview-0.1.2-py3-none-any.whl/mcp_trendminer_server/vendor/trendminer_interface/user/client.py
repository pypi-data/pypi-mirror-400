import abc
from .user import UserFactory



class UserClient(abc.ABC):
    """Client for UserFactory"""
    @property
    def user(self):
        """Factory for retrieving users

        Returns
        -------
        UserFactory
        """
        return UserFactory(client=self)
