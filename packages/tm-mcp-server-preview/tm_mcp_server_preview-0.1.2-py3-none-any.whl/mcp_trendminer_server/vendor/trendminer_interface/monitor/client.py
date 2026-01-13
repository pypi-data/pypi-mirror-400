import abc
from .monitor import MonitorFactory


class MonitorClient(abc.ABC):
    """Monitor Client"""
    @property
    def monitor(self):
        """Factory for monitors

        Returns
        -------
        MonitorFactory
        """
        return MonitorFactory(client=self)
