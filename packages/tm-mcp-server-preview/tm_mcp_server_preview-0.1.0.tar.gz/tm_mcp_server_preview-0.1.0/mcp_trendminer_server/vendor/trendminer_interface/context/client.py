import abc

from .field import ContextFieldFactory
from .workflow import ContextWorkflowFactory
from .type import ContextTypeFactory
from .item import ContextItemFactory
from .view import ContextHubViewFactory
from .filter import ContextFilterMultiFactory

from trendminer_interface.base import AuthenticatableBase


class ContextClient(abc.ABC):
    """Context client"""
    @property
    def context(self):
        """Factory for objects related to ContextHub and context items

        Returns
        -------
        ContextFactory
        """
        return ContextFactory(client=self)


class ContextFactory(AuthenticatableBase):
    """Factory for objects related to ContextHub and context items"""
    @property
    def field(self):
        """Factory for context fields

        Returns
        -------
        ContextFieldFactory
        """
        return ContextFieldFactory(client=self.client)

    @property
    def workflow(self):
        """Factory for context workflows

        Returns
        -------
        ContextWorkflowFactory
        """
        return ContextWorkflowFactory(client=self.client)

    @property
    def type(self):
        """Factory for context types

        Returns
        -------
        ContextTypeFactory
        """
        return ContextTypeFactory(client=self.client)

    @property
    def item(self):
        """Factory for context items

        Returns
        -------
        ContextItemFactory
        """
        return ContextItemFactory(client=self.client)

    @property
    def view(self):
        """Factory for ContextHub views

        Returns
        -------
        ContextHubViewFactory
        """
        return ContextHubViewFactory(client=self.client)

    @property
    def filter(self):
        """Factory for ContextHub filters used in ContextHub views

        Returns
        -------
        ContextFilterMultiFactory
        """
        return ContextFilterMultiFactory(client=self.client)
