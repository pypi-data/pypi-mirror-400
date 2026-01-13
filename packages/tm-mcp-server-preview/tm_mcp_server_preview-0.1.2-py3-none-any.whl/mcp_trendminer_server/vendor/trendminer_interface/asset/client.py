import abc
from .asset import AssetFactory
from .attribute import AttributeFactory


class AssetClient(abc.ABC):
    """Asset client"""

    @property
    def asset(self):
        """Factory for retrieving assets

        Returns
        -------
        AssetFactory
        """
        return AssetFactory(client=self)

    @property
    def attribute(self):
        """Factory for retrieving attributes

        Returns
        -------
        AttributeFactory
        """
        return AttributeFactory(client=self)