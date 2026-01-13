from trendminer_interface.base import AuthenticatableBase
from .tag import TagIOFactory


class IOClient:
    """Client for input-output factory"""
    @property
    def io(self):
        """Input-output factory

        Returns
        -------
        IOFactory
        """
        return IOFactory(client=self)


class IOFactory(AuthenticatableBase):
    """Input-output factory"""
    @property
    def tag(self):
        """Factory for tag import

        Returns
        -------
        TagIOFactory
        """
        return TagIOFactory(client=self.client)
