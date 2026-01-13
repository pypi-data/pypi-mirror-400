import abc

from .dashboard import DashboardFactory


class DashHubClient(abc.ABC):
    """Client for DashboardFactory"""
    @property
    def dashboard(self):
        """Factory for dashboard-related objects"""
        return DashboardFactory(client=self)
