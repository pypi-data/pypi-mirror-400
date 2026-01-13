import abc

from trendminer_interface.base import AuthenticatableBase
from .chart import ChartingPropertiesFactory
from .view import TrendHubViewFactory
from .group import TrendHubEntryGroupFactory


class TrendHubClient(abc.ABC):
    """Client for TrendHubFactory"""
    @property
    def trend(self):
        """Parent factory for TrendHub-related objects

        Returns
        -------
        TrendHubFactory
        """
        return TrendHubFactory(client=self)


class TrendHubFactory(AuthenticatableBase):
    """Parent factory for TrendHub-related factories"""
    @property
    def chart(self):
        """Parent factory for TrendHub charting properties

        Returns
        -------
        ChartingPropertiesFactory
        """
        return ChartingPropertiesFactory(client=self.client)

    @property
    def view(self):
        """Factory for TrendHub views

        Returns
        -------
        TrendHubViewFactory
        """
        return TrendHubViewFactory(client=self.client)

    @property
    def group(self):
        """Factory for TrendHub view entry groups

        A group consists of two or more tags and/or attributes grouped together in TrendHub.

        Returns
        -------
        TrendHubEntryGroupFactory
        """
        return TrendHubEntryGroupFactory(client=self.client)
